const Results = require('./Results')
const L = require('./Logger')('Import Comments')
const jsonQuery = require('json-query')

const issueNumberExists = (data, issueNumber) => {
    return jsonQuery(`[issueNumber=${issueNumber}].id`, {data}).value != null
}

const enrichWithIssueNumber = (arr, issueNumber) => {
    return arr.map(o => {return {...o, issueNumber}})
}

module.exports = (owner, repo, inputIssues, output, github) => {

    const subject = `${owner}/${repo}/${output}`
    const issues = Results.read(owner, repo, inputIssues)
    let comments = Results.exists(owner, repo, output) ? Results.read(owner, repo, output) : []

    L.log(`Start: ${subject}`)

    return new Promise((resolve, reject) => {

        const ongoingImports = []

        issues.forEach(i => {
            const number = i.number

            if (i.comments == 0) {
                L.log(`No comments for ${number}`)
                return
            }
    
            if (issueNumberExists(comments, number)) {
                L.log(`${number} already exists in ${subject}`)
                return
            }
    
            const promise = github
                .getIssues(owner, repo)
                .listIssueComments(number)
                .then(data => {
                    const enrichedData = enrichWithIssueNumber(data.data, number)
                    comments = [...comments, ...enrichedData]
                    L.log(`Imported [${enrichedData.map(c => c.id).join(",")}]`)
                })
                .catch(error => {
                    L.err(`During ${subject}`)
                    L.err(error.message)
                })
            
            ongoingImports.push(promise)
        })

        const saveResult = () => {
            Results.save(owner, repo, output, comments)
            L.log(`Saved ${subject}`)
        }

        return Promise
            .all(ongoingImports)
            .then(() => {
                saveResult()
                resolve()
            })
            .catch(() => {
                saveResult()
                reject()
            })
    })

}