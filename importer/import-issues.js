const Results = require('./Results')
const L = require('./Logger')('Import Issues')

module.exports = (owner, repo, output, github) => {
    
    const subject = `${owner}/${repo}/${output}`

    return new Promise((resolve, reject) => {

        if (Results.exists(owner, repo, output)) {
            L.log(`Skipping ${subject}`)
            return resolve()
        }
        
        L.log(`Start: ${subject}`)
    
        github
            .getIssues(owner, repo)
            .listIssues({
                filter: 'all',
                state: 'closed'
            })
            .then(data => {
                Results.save(owner, repo, output, data.data)
                L.log(`Finished ${subject}`)
                return resolve()
            })
            .catch(error => {
                L.err(`During ${subject}`)
                L.err(error.message)
                return reject()
            })
    })
}