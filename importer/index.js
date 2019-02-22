const GitHub = require('github-api')

process.env.IMPORT_RESULT_PATH = process.env.IMPORT_RESULT_PATH || 'result/'
const owner = process.env.IMPORT_OWNER || 'jquery'
const repo = process.env.IMPORT_REPO || 'jquery'
const subject = process.env.IMPORT_SUBJECT || 'mgr'

const github = new GitHub({
    username: 'PiotrSliwa',
    token: '33568e2691e6d1e97e156f00c622ca76761e9df6'
})

const issues = `${subject}-issues`
const pulls = `${subject}-pulls`
const comments = `${subject}-comments`
const processed = `${subject}-processed`

require('./import-issues')(owner, repo, issues, github).then(() => {
    require('./import-pulls')(owner, repo, issues, pulls, github).then(() => {
        require('./import-comments')(owner, repo, issues, comments, github).then(() => {
            require('./process-imports')(owner, repo, issues, pulls, comments, processed, github).then(() => {
                console.log('FINISHED ALL')
            })
        })
    })
})
