function getSuccessRateColor(successRate) {
    if (successRate >= 80) {
        return "green";
    } else if (successRate >= 60) {
        return "yellow";
    } else if (successRate >= 40) {
        return "orange";
    } else {
        return "red";
    }
}

document.addEventListener("DOMContentLoaded", function () {
    // Apply color directly
    document.querySelectorAll(".success-rate").forEach((element) => {
        const successRate = parseInt(element.dataset.rate, 10);
        element.style.color = getSuccessRateColor(successRate);
    });
});

console.log("Script loaded!");