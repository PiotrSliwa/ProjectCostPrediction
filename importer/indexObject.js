module.exports = (key, arr) => {
    const result = {}
    arr.forEach(o => {
        result[o[key]] = o
    })
    return result
}