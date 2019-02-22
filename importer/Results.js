const fs = require('fs')
const jsonfile = require('jsonfile')
const L = require('./Logger')('Results')

const getFilename = (owner, repo, name) => {
    return `${process.env.IMPORT_RESULT_PATH}${owner}_${repo}_${name}.json`
}

module.exports = {
    exists: (owner, repo, name) => {
        const filename = getFilename(owner, repo, name)
        if (fs.existsSync(filename)) {
            L.log(`${filename} exists`)
            return true
        }
        return false
    },

    save: (owner, repo, name, json) => {
        const filename = getFilename(owner, repo, name)
        jsonfile.writeFileSync(filename, json, {spaces: 2})
        L.log(`Saved ${filename}`)
    },

    read: (owner, repo, name) => {
        const filename = getFilename(owner, repo, name)
        L.log(`Read ${filename}`)
        return jsonfile.readFileSync(filename)
    }
}