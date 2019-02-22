const stringifyObject = require('stringify-object');

const encode = (name, o) => {
    const str = stringifyObject(o, {
        indent: '  ',
        singleQuotes: false
    })
    return `${name}: ${str}`
}

module.exports = name => {
    return {
        log: o => console.log(encode(name, o)),
        err: o => console.error(`ERROR: ${encode(name, o)}`)
    }
}