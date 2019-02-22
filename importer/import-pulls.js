const Results = require('./Results')
const L = require('./Logger')('Import Pull Requests')
const jsonQuery = require('json-query')

const numberExists = (data, number) => {
    return jsonQuery(`[number=${number}].id`, {data}).value != null
}

module.exports = (owner, repo, inputIssues, output, github) => {

    const subject = `${owner}/${repo}/${output}`
    const issues = Results.read(owner, repo, inputIssues)
    const pulls = Results.exists(owner, repo, output) ? Results.read(owner, repo, output) : []

    L.log(`Start: ${subject}`)

    return new Promise((resolve, reject) => {

        const ongoingImports = []

        issues.forEach(i => {
            const number = i.number
    
            if (numberExists(pulls, number)) {
                L.log(`${number} already exists in ${subject}`)
                return
            }
            
            if (!i.hasOwnProperty('pull_request')) {
                L.log(`${number} is not a PR`)
                return
            }
    
            const promise = github
                .getRepo(owner, repo)
                .getPullRequest(number)
                .then(data => {
                    pulls.push(data.data)
                    L.log(`Imported ${data.data.number}`)
                })
                .catch(error => {
                    L.err(`During ${subject}`)
                    L.err(error.message)
                })
            
            ongoingImports.push(promise)
        })

        const saveResult = () => {
            Results.save(owner, repo, output, pulls)
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