const Results = require('./Results')
const L = require('./Logger')('Process Imports')
const jsonQuery = require('json-query')
const indexObject = require('./indexObject')

module.exports = (owner, repo, inputIssues, inputPulls, inputComments, output, github) => {
    return new Promise((resolve, reject) => {

        const subject = `${owner}/${repo}/${output}`
        
        L.log(`Start: ${subject}`)

        const issueIndex = indexObject('number', Results.read(owner, repo, inputIssues))
        const comments = Results.read(owner, repo, inputComments)
        const pulls = Results.read(owner, repo, inputPulls)

        const getAllReferences = contents => {
            let g;
            const result = new Set()
            const r = /#(\d+)/g
            while (g = r.exec(contents.join())) {
                const number = g[1]
                if (issueIndex[number] === undefined) {
                    L.log(`Referenced issue ${number} does not exist`)
                    continue
                }
                result.add(parseInt(number))
            }
            return [...result]
        }

        const subComments = issueNumber => {
            return jsonQuery(`[*issueNumber=${issueNumber}][*]`, {data: comments}).value.map(c => {
                return {
                    id: c.id,
                    author: c.user.login,
                    author_association: c.author_association,
                    body: c.body
                }
            })
        }

        const subIssues = numbers => {
            return numbers
                .map(n => {
                    const issue = issueIndex[n.toString()]
                    if (issue.hasOwnProperty('pull_request'))
                        return null
                    return {
                        number: n,
                        title: issue.title,
                        body: issue.body,
                        comments: subComments(n)
                    }
                })
                .filter(i => i !== null)
        }

        const extractBodies = arr => {
            return arr.map(o => o.body)
        }
        
        const processBase = p => {
            const comments = subComments(p.number)
            const references = getAllReferences([p.title, p.body, ...extractBodies(comments)])
            return {
                number: p.number,
                milestone: p.milestone ? p.milestone.title : null,
                author: p.user.login,
                author_association: p.author_association,
                labels: p.labels.map(i => i.name),
                title: p.title,
                body: p.body,
                comments,
                references,
                refIssues: subIssues(references)
            }
        }
        
        const result = pulls.map(p => {
            return {
                ...processBase(p, issueIndex),
                additions: p.additions,
                deletions: p.deletions
            }
        })

        Results.save(owner, repo, output, result)

        resolve()
    })
}