
/**
 * @fileoverview A collection of utility functions.
 */

/**
 * Simple compare function.
 * @param {object} a - first object
 * @param {number} a.x - first number
 * @param {object} b - second object
 * @param {number} b.x - second number
 * @return {number} 0 if equal, 1 if a.x > b.x, -1 if a.x < b.x
 */
function compareX(a, b) {
    if (a.x < b.x)
        return -1;
    if (a.x > b.x)
        return 1;
    return 0;
}

/**
 * Format Mbp to two decimal places.
 * @param {number} Mbp - the number to round
 * @return {string} Mbp formatted to two decimal places
 */
function formatMbp(Mbp) {
    return Number(Mbp).toFixed(2);
}


/**
 * Get a random integer between min and max.
 * @param {number} minn - the number to round
 * @param {number} maxx - the number to round
 * @return {number} a number between minn and maxx
 */
function getRandomInt(minn, maxx) {
    minn = Math.ceil(minn);
    maxx = Math.floor(maxx);
    return Math.floor(Math.random() * (maxx - minn + 1)) + minn;
}



/**
 * Permutate arrays.
 * Example:
 *     let p = permutateArrays(['1', '2', '3'], ['A', 'B']]);
 *     console.log(p);
 *     [['1', 'A'], ['1', 'B'],
 *      ['2', 'A'], ['2', 'B'],
 *      ['3', 'A'], ['3', 'B']]
 *
 * Adapted from:
 * https://stackoverflow.com/questions/15298912/javascript-generating-combinations-from-n-arrays-with-m-elements
 *
 * @param arraysToCombine {Array} - array of arrays
 * @returns {Array} permutated array
 */
function permutateArrays(arraysToCombine) {
    let divisors = [];
    for (let i = arraysToCombine.length - 1; i >= 0; i--) {
        divisors[i] = divisors[i + 1]
            ? divisors[i + 1] * arraysToCombine[i + 1].length
            : 1;
    }

    function getPermutation(n, arraysToCombine) {
        let result = [];
        let curArray;
        for (let i = 0; i < arraysToCombine.length; i++) {
            curArray = arraysToCombine[i];
            result.push(
                curArray[Math.floor(n / divisors[i]) % curArray.length]
            );
        }
        return result;
    }

    let numPerms = arraysToCombine[0].length;
    for (let i = 1; i < arraysToCombine.length; i++) {
        numPerms *= arraysToCombine[i].length;
    }

    let combinations = [];
    for (let i = 0; i < numPerms; i++) {
        combinations.push(getPermutation(i, arraysToCombine));
    }
    return combinations;
}


/**
 * Get the mean of an array of numbers.
 * @param data {Array} - array of numbers
 * @returns {number} mean of "data"
 */
function mean(data) {
    let len = data.length;
    let sum = 0;
    for (let i = 0; i < len; i++) {
        sum += parseFloat(data[i]);
    }
    return (sum / len);
}


/**
 * Because .sort() doesn't sort numbers correctly
 * @param a {number} - 1st value to compare
 * @param b {number} - 2nd value to compare
 * @returns {number} positive, negative, or zero
 */
function numSort(a, b) {
    return a - b;
}


/**
 * Get any percentile from an array.
 * @param data {Array} - array of numbers
 * @param percentile {number} - which percentile to get
 * @returns {number} the "percentile" of "data"
 */
function getPercentile(data, percentile) {
    data.sort(numSort);
    let index = (percentile/100) * data.length;
    let result;
    if (Math.floor(index) === index) {
         result = (data[(index-1)] + data[index])/2;
    }
    else {
        result = data[Math.floor(index)];
    }
    return result;
}


/**
 * Wrap the percentile calls in one method.
 * @param data {Array} - array of numbers
 * @returns {{low: number, q1: number, median: number, q3: number, high: number}}
 */
function getBoxValues(data) {
    let filteredData = [];

    $.each(data, function(idx, elem) {
        if (!isNaN(elem)) {
            filteredData.push(elem);
        }
    });

    return {low: Math.min.apply(Math, filteredData),
            q1: getPercentile(filteredData, 25),
            median: getPercentile(filteredData, 50),
            q3: getPercentile(filteredData, 75),
            high: Math.max.apply(Math, filteredData)};
}


/**************************************************************************
 **
 ** LAYOUT ALGORITHMS
 **
 *************************************************************************/

/**
 * If the slot has space or not.
 * @param {Object} feature - the feature to check
 * @param {number} feature.position_start - the strat position
 * @param {number} feature.end - the end position
 * @param {Array} featuresInSlot - an array of features in this slot
 * @return {boolean} true if slot has space for the feature
 */
function slotHasSpace(feature, featuresInSlot, spacing) {
    if (!featuresInSlot) {
        return true;
    }

    for (let i = 0; i < featuresInSlot.length; i++) {
        let subject = featuresInSlot[i];


        if (((feature.position_start - spacing <= subject.position_start) &&
                (feature.max_end + spacing >= subject.position_start)) ||
            ((feature.position_start - spacing >= subject.position_start) &&
                (feature.position_start - spacing <= subject.max_end))) {
            return false;
        }
    }

    return true;
}

/**
 * Sort the features by the slot.
 * @param {Array} features - an array of features in this slot
 * @return {Array} the sorted slots
 */
function sortFeaturesBySlot(features) {
    let slots = [];
    for (let i = 0; i < features.length; i++) {
        let feature = features[i];
        if (!slots[feature.slot]) {
            slots[feature.slot] = [];
        }
        slots[feature.slot].push(feature);
    }
    return slots;
}

/**
 * Determine where each feature should be located.
 * @param {Array} features - an array of features
 */
function layoutFeatures(features, spacing=0) {
    let allocated = [];
    let remaining = features;
    let neededSlots = 0;

    for (let i = 0; i < remaining.length; i++) {
        let featuresBySlot = sortFeaturesBySlot(allocated);
        let current = remaining[i];
        let slot = 0;
        while (true) {
            if (slotHasSpace(current, featuresBySlot[slot], spacing)) {
                current.slot = slot;
                allocated.push(current);
                if (slot > neededSlots) {
                    neededSlots = slot;
                }
                break;
            }
            slot++;
        }
    }
}
