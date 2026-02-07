// ======================
// BuildAI Pro – script.js
// ======================

// Scroll helper
function scrollToCalculator() {
    document.getElementById("calculator").scrollIntoView({ behavior: "smooth" });
}

// Main form handler
document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("projectForm");

    if (!form) return;

    form.addEventListener("submit", function (e) {
        e.preventDefault();

        // Read inputs
        const area = Number(document.getElementById("builtUpArea").value);
        const floorsText = document.getElementById("floors").value;
        const duration = Number(document.getElementById("days").value);

        // Convert floors
        let floors = 1;
        if (floorsText && floorsText !== "G") {
            floors = parseInt(floorsText.replace("G+", ""));
        }

        // Button state
        const button = document.querySelector(".submit-button");
        button.textContent = "Calculating...";
        button.disabled = true;

        // Hide old results
        const resultsSection = document.getElementById("results");
        if (resultsSection) {
            resultsSection.style.display = "none";
        }

        // Call Flask backend
        fetch("/estimate", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                area: area,
                floors: floors,
                duration: duration
            })
        })
        .then(response => {
            if (!response.ok) {
                throw new Error("Backend error");
            }
            return response.json();
        })
        .then(data => {
            // Show results section
            document.getElementById("results").style.display = "block";

            // Fill workforce
            document.getElementById("workersTotal").textContent =
                data.calculations.workers.total_workers ?? data.calculations.workers.total;

            // Fill materials
            document.getElementById("cement").textContent =
                data.calculations.materials.cement_bags;

            document.getElementById("steel").textContent =
                data.calculations.materials.steel_tons;

            // Fill cost
            document.getElementById("totalCost").textContent =
                data.calculations.cost.total_cost;

            // Fill timeline
            document.getElementById("timeline").textContent =
                data.calculations.timeline.finishing;

            // AI insights
            document.getElementById("aiInsights").textContent =
                data.ai_insights;

            // Reset button
            button.textContent = "Calculate Project";
            button.disabled = false;

            // Scroll to results
            document.getElementById("results")
                .scrollIntoView({ behavior: "smooth" });
        })
        .catch(error => {
            console.error(error);
            alert("❌ Failed to connect to AI backend");

            button.textContent = "Calculate Project";
            button.disabled = false;
        });
    });
});