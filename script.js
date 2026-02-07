// script.js

function scrollToCalculator() {
    document.getElementById('calculator').scrollIntoView({ behavior: 'smooth' });
}

function handleLogout() {
    localStorage.clear();
    window.location.href = 'index.html';
}

document.addEventListener('DOMContentLoaded', function() {
    const projectForm = document.getElementById('projectForm');
    
    if (projectForm) {
        projectForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const formData = {
                builtUpArea: parseInt(document.getElementById('builtUpArea').value),
                floors: document.getElementById('floors').value,
                budget: parseInt(document.getElementById('budget').value),
                days: parseInt(document.getElementById('days').value),
                timestamp: new Date().toISOString()
            };
            
            const calculations = calculateProject(formData);
            
            localStorage.setItem('projectData', JSON.stringify(formData));
            localStorage.setItem('calculations', JSON.stringify(calculations));
            
            window.location.href = 'result.html';
        });
    }
});

function calculateProject(data) {
    const floorMultiplier = {
        'G': 1,
        'G+1': 2,
        'G+2': 3,
        'G+3': 4,
        'G+4': 5
    };
    
    const floors = floorMultiplier[data.floors] || 1;
    const totalArea = data.builtUpArea * floors;
    
    const workersPerSqFt = 0.01;
    const totalWorkers = Math.ceil(totalArea * workersPerSqFt);
    const skilledWorkers = Math.ceil(totalWorkers * 0.35);
    const semiSkilledWorkers = Math.ceil(totalWorkers * 0.30);
    const unskilledWorkers = Math.ceil(totalWorkers * 0.30);
    const supervisors = Math.ceil(totalWorkers * 0.05);
    
    const materialCost = Math.ceil(data.budget * 0.45);
    const laborCost = Math.ceil(data.budget * 0.35);
    const equipmentCost = Math.ceil(data.budget * 0.12);
    const miscCost = Math.ceil(data.budget * 0.08);
    
    const cementBags = Math.ceil(totalArea * 0.4);
    const sandTons = Math.ceil(totalArea * 0.045);
    const aggregateTons = Math.ceil(totalArea * 0.09);
    const steelKg = Math.ceil(totalArea * 8);
    const bricks = Math.ceil(totalArea * 50);
    
    const weeks = Math.ceil(data.days / 7);
    const foundationWeeks = Math.ceil(weeks * 0.25);
    const structureWeeks = Math.ceil(weeks * 0.50);
    const finishingWeeks = Math.ceil(weeks * 0.25);
    
    return {
        workers: {
            total: totalWorkers,
            skilled: skilledWorkers,
            semiSkilled: semiSkilledWorkers,
            unskilled: unskilledWorkers,
            supervisors: supervisors
        },
        costs: {
            total: data.budget,
            materials: materialCost,
            labor: laborCost,
            equipment: equipmentCost,
            misc: miscCost
        },
        materials: {
            cement: cementBags,
            sand: sandTons,
            aggregate: aggregateTons,
            steel: steelKg,
            bricks: bricks
        },
        timeline: {
            weeks: weeks,
            foundation: foundationWeeks,
            structure: structureWeeks,
            finishing: finishingWeeks
        },
        totalArea: totalArea,
        floors: floors
    };
}

function loadDashboardData() {
    const projectData = JSON.parse(localStorage.getItem('projectData'));
    const calculations = JSON.parse(localStorage.getItem('calculations'));
    
    if (!projectData || !calculations) {
        window.location.href = 'index.html';
        return;
    }
    
    document.getElementById('summaryArea').textContent = projectData.builtUpArea.toLocaleString() + ' sq.ft';
    document.getElementById('summaryFloors').textContent = projectData.floors;
    document.getElementById('summaryBudget').textContent = '₹' + projectData.budget.toLocaleString();
    document.getElementById('summaryDays').textContent = projectData.days + ' days';
    
    document.getElementById('totalWorkers').textContent = calculations.workers.total;
    document.getElementById('skilledWorkers').textContent = calculations.workers.skilled;
    document.getElementById('semiSkilledWorkers').textContent = calculations.workers.semiSkilled;
    document.getElementById('unskilledWorkers').textContent = calculations.workers.unskilled;
    document.getElementById('supervisors').textContent = calculations.workers.supervisors;
    
    document.getElementById('totalCost').textContent = '₹' + calculations.costs.total.toLocaleString();
    document.getElementById('materialCost').textContent = '₹' + calculations.costs.materials.toLocaleString();
    document.getElementById('laborCost').textContent = '₹' + calculations.costs.labor.toLocaleString();
    document.getElementById('equipmentCost').textContent = '₹' + calculations.costs.equipment.toLocaleString();
    document.getElementById('miscCost').textContent = '₹' + calculations.costs.misc.toLocaleString();
    
    document.getElementById('cementQty').textContent = calculations.materials.cement.toLocaleString() + ' bags (50kg)';
    document.getElementById('sandQty').textContent = calculations.materials.sand.toLocaleString() + ' tons';
    document.getElementById('aggregateQty').textContent = calculations.materials.aggregate.toLocaleString() + ' tons';
    document.getElementById('steelQty').textContent = calculations.materials.steel.toLocaleString() + ' kg';
    document.getElementById('brickQty').textContent = calculations.materials.bricks.toLocaleString() + ' units';
    
    document.getElementById('foundationWeeks').textContent = calculations.timeline.foundation + ' weeks';
    document.getElementById('structureWeeks').textContent = calculations.timeline.structure + ' weeks';
    document.getElementById('finishingWeeks').textContent = calculations.timeline.finishing + ' weeks';
}

function loadScheduleData() {
    const projectData = JSON.parse(localStorage.getItem('projectData'));
    const calculations = JSON.parse(localStorage.getItem('calculations'));
    
    if (!projectData || !calculations) {
        window.location.href = 'index.html';
        return;
    }
    
    document.getElementById('scheduleWeeks').textContent = calculations.timeline.weeks + ' weeks';
    document.getElementById('totalTasks').textContent = (calculations.timeline.weeks * 3).toString();
    
    const timeline = document.getElementById('scheduleTimeline');
    
    const phases = [
        {
            icon: '🏗️',
            title: 'Foundation Phase',
            duration: calculations.timeline.foundation + ' weeks',
            weeks: generateFoundationWeeks(calculations.timeline.foundation)
        },
        {
            icon: '🏢',
            title: 'Structure Phase',
            duration: calculations.timeline.structure + ' weeks',
            weeks: generateStructureWeeks(calculations.timeline.structure, calculations.timeline.foundation)
        },
        {
            icon: '🎨',
            title: 'Finishing Phase',
            duration: calculations.timeline.finishing + ' weeks',
            weeks: generateFinishingWeeks(calculations.timeline.finishing, calculations.timeline.foundation + calculations.timeline.structure)
        }
    ];
    
    phases.forEach(phase => {
        const phaseSection = document.createElement('div');
        phaseSection.className = 'phase-section';
        
        phaseSection.innerHTML = `
            <div class="phase-header">
                <div class="phase-icon">${phase.icon}</div>
                <div class="phase-info">
                    <div class="phase-title">${phase.title}</div>
                    <div class="phase-duration">${phase.duration}</div>
                </div>
            </div>
            <div class="week-list">
                ${phase.weeks.map(week => `
                    <div class="week-item">
                        <div class="week-header">${week.title}</div>
                        <div class="week-tasks">${week.tasks}</div>
                    </div>
                `).join('')}
            </div>
        `;
        
        timeline.appendChild(phaseSection);
    });
}

function generateFoundationWeeks(totalWeeks) {
    const weeks = [];
    const weeksPerTask = Math.ceil(totalWeeks / 4);
    
    const tasks = [
        { title: 'Week 1-' + weeksPerTask, tasks: 'Site survey, soil testing, marking & excavation' },
        { title: 'Week ' + (weeksPerTask + 1) + '-' + (weeksPerTask * 2), tasks: 'Foundation laying, PCC work, footing construction' },
        { title: 'Week ' + (weeksPerTask * 2 + 1) + '-' + (weeksPerTask * 3), tasks: 'Column reinforcement, plinth beam casting' },
        { title: 'Week ' + (weeksPerTask * 3 + 1) + '-' + totalWeeks, tasks: 'Backfilling, plinth level completion, curing' }
    ];
    
    return tasks.slice(0, Math.min(4, totalWeeks));
}

function generateStructureWeeks(totalWeeks, offset) {
    const weeks = [];
    const weeksPerFloor = Math.ceil(totalWeeks / 3);
    
    const tasks = [
        { title: 'Week ' + (offset + 1) + '-' + (offset + weeksPerFloor), tasks: 'Column casting, beam formwork, slab reinforcement' },
        { title: 'Week ' + (offset + weeksPerFloor + 1) + '-' + (offset + weeksPerFloor * 2), tasks: 'Slab casting, brick masonry, plastering preparation' },
        { title: 'Week ' + (offset + weeksPerFloor * 2 + 1) + '-' + (offset + totalWeeks), tasks: 'Additional floors, staircase construction, structural completion' }
    ];
    
    return tasks;
}

function generateFinishingWeeks(totalWeeks, offset) {
    const weeks = [];
    const weeksPerTask = Math.ceil(totalWeeks / 4);
    
    const tasks = [
        { title: 'Week ' + (offset + 1) + '-' + (offset + weeksPerTask), tasks: 'Internal plastering, external plastering, waterproofing' },
        { title: 'Week ' + (offset + weeksPerTask + 1) + '-' + (offset + weeksPerTask * 2), tasks: 'Electrical wiring, plumbing installation, door/window fitting' },
        { title: 'Week ' + (offset + weeksPerTask * 2 + 1) + '-' + (offset + weeksPerTask * 3), tasks: 'Flooring, tiling, painting preparation' },
        { title: 'Week ' + (offset + weeksPerTask * 3 + 1) + '-' + (offset + totalWeeks), tasks: 'Final painting, fixture installation, cleanup & handover' }
    ];
    
    return tasks.slice(0, Math.min(4, totalWeeks));
}

function loadBlueprintData() {
    const projectData = JSON.parse(localStorage.getItem('projectData'));
    const calculations = JSON.parse(localStorage.getItem('calculations'));
    
    if (!projectData || !calculations) {
        window.location.href = 'index.html';
        return;
    }
    
    const projectId = 'BP-' + Date.now().toString(36).toUpperCase();
    document.getElementById('projectId').textContent = projectId;
    document.getElementById('blueprintArea').textContent = calculations.totalArea.toLocaleString() + ' sq.ft';
    document.getElementById('blueprintFloors').textContent = projectData.floors;
    
    const container = document.getElementById('blueprintContainer');
    
    for (let i = 0; i < calculations.floors; i++) {
        const floorPlan = createFloorPlan(i, projectData.builtUpArea);
        container.appendChild(floorPlan);
    }
}

function createFloorPlan(floorNumber, area) {
    const floorDiv = document.createElement('div');
    floorDiv.className = 'floor-plan';
    
    const floorName = floorNumber === 0 ? 'Ground Floor' : `Floor ${floorNumber}`;
    
    const rooms = generateRooms(floorNumber, area);
    
    floorDiv.innerHTML = `
        <div class="floor-title">${floorName}</div>
        <div class="floor-grid">
            ${rooms.map(room => `
                <div class="room ${room.type}">
                    <div class="room-name">${room.name}</div>
                    <div class="room-size">${room.size}</div>
                </div>
            `).join('')}
        </div>
    `;
    
    return floorDiv;
}

function generateRooms(floorNumber, baseArea) {
    const roomTemplates = [
        { name: 'Living Room', type: 'living', sizeRatio: 0.25 },
        { name: 'Master Bedroom', type: 'bedroom', sizeRatio: 0.20 },
        { name: 'Bedroom 2', type: 'bedroom', sizeRatio: 0.15 },
        { name: 'Kitchen', type: 'kitchen', sizeRatio: 0.12 },
        { name: 'Bathroom 1', type: 'bathroom', sizeRatio: 0.08 },
        { name: 'Bathroom 2', type: 'bathroom', sizeRatio: 0.06 },
        { name: 'Utility', type: 'utility', sizeRatio: 0.08 },
        { name: 'Balcony', type: 'living', sizeRatio: 0.06 }
    ];
    
    if (floorNumber > 0) {
        return roomTemplates.map(room => ({
            name: room.name,
            type: room.type,
            size: Math.ceil(baseArea * room.sizeRatio) + ' sq.ft'
        }));
    } else {
        return roomTemplates.map(room => ({
            name: room.name,
            type: room.type,
            size: Math.ceil(baseArea * room.sizeRatio) + ' sq.ft'
        }));
    }
}