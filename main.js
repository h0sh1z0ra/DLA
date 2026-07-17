// Canvas elements
// For cluster
const canvas_cluster = document.getElementById("canvas_cluster");
const ctx_cluster = canvas_cluster.getContext("2d");

// For particle path
const canvas_path = document.getElementById("canvas_path");
const ctx_path = canvas_path.getContext("2d");

canvas_path.style.display = "none";     // Hide by default
ctx_path.fillStyle = "rgb(200 0 0/30%)";

let running = true;

// ====================================================================== //
// DLA variables
let x = 0;
let y = 0;
let R_max = 0;
let Pnn = 1;
let Psnn = 0;

// Lists
let nn_list = [[1,0],[-1,0],[0,1],[0,-1]];
let snn_list = [[1,1],[-1,1],[1,-1],[-1,-1]];

// Sliders
let pnnValue = document.getElementById("pnnValue");
const pnnSlider = document.getElementById("pnnSlider"); 
pnnSlider.addEventListener("input", () => {     // () = callback; parameter list. => makes it a function
    Pnn = parseFloat(pnnSlider.value);          // convert to float
    pnnValue.textContent = Pnn;
    console.log(`Pnn = ${Pnn}`);
});

let psnnValue = document.getElementById("psnnValue");
const psnnSlider = document.getElementById("psnnSlider"); 
psnnSlider.addEventListener("input", () => {    
    Psnn = parseFloat(psnnSlider.value);   
    psnnValue.textContent = Psnn;  
    console.log(`Psnn = ${Psnn}`);
});

function bindButton(id, callback) {
    let element = document.getElementById(id);
    element.addEventListener("click", () => {
        callback();
    }
)};

bindButton("pauseButton", () => {
    running = !running;
    pauseButton.textContent = running ? "Pause" : "Resume";
    pauseButton.classList.toggle("active");
});

// ====================================================================== //
// Frame rate control
let STEPS_PER_FRAME = 224;

const stepsPerFrame = document.getElementById("stepsPerFrame"); 
stepsPerFrame.addEventListener("input", () => {                 // () = callback; parameter list. => makes it a function
    // STEPS_PER_FRAME = parseFloat(stepsPerFrame.value);          // convert to float
    STEPS_PER_FRAME = Math.round(1 * (50000/1)**stepsPerFrame.value);
    console.log(STEPS_PER_FRAME);
});

// ====================================================================== //
// Bias
let direction;
let delta = 0; // bias strength
let p_list = [0.25, 0.25, 0.25, 0.25];
let drn_map = ["left", "right", "up", "down"];

function addBias(direction, delta) {
    prob_list = [0.25, 0.25, 0.25, 0.25];

    if (direction % 2 == 0) {
        prob_list[direction] += delta;
        prob_list[direction+1] -= delta;
    }

    else {
        prob_list[direction] += delta;
        prob_list[direction-1] -= delta;
    }

    return prob_list;
}

let biasStrengthLabel = document.getElementById("biasStrengthLabel");
biasStrengthLabel.style.display = "none"; // hide by default

// Adding bias direction buttons
bindButton("biasNone", () => { 
    delta = 0; 
    p_list = [0.25,0.25,0.25,0.25];
    biasSlider.value = delta; 

    biasStrengthLabel.style.display = "none";
    biasSlider.style.display="none";

    biasNone.classList.add("active");
    biasRight.classList.remove("active");
    biasDown.classList.remove("active");
    biasUp.classList.remove("active");
    biasLeft.classList.remove("active");

    console.log(`p_list = ${p_list}, direction = ${drn_map[direction]}, strength = ${delta}`)
});

bindButton("biasLeft", () => { 
    direction = 0; 
    delta = 0.08;
    biasSlider.value = delta;  
    p_list = addBias(direction, delta); 

    biasStrengthLabel.style.display = "";
    biasSlider.style.display=""; 

    biasNone.classList.remove("active");
    biasLeft.classList.add("active");
    biasRight.classList.remove("active");
    biasDown.classList.remove("active");
    biasUp.classList.remove("active");

    console.log(`p_list = ${p_list}, direction = ${drn_map[direction]}, strength = ${delta}`)
});

bindButton("biasRight", () => { 
    direction = 1; 
    delta = 0.08;
    biasSlider.value = delta;  
    p_list = addBias(direction, delta); 

    biasStrengthLabel.style.display = "";
    biasSlider.style.display=""; 

    biasNone.classList.remove("active");
    biasRight.classList.add("active");
    biasDown.classList.remove("active");
    biasUp.classList.remove("active");
    biasLeft.classList.remove("active");

    console.log(`p_list = ${p_list}, direction = ${drn_map[direction]}, strength = ${delta}`) 
});

bindButton("biasUp", () => { 
    direction = 2; 
    delta = 0.08;
    biasSlider.value = delta;  
    p_list = addBias(direction, delta); 

    biasStrengthLabel.style.display = "";
    biasSlider.style.display=""; 

    biasNone.classList.remove("active");
    biasUp.classList.add("active");
    biasDown.classList.remove("active");
    biasLeft.classList.remove("active");
    biasRight.classList.remove("active");

    console.log(`p_list = ${p_list}, direction = ${drn_map[direction]}, strength = ${delta}`) 
});

bindButton("biasDown", () => { 
    direction = 3; 
    delta = 0.08;
    biasSlider.value = delta;  
    p_list = addBias(direction, delta);

    biasStrengthLabel.style.display = "";
    biasSlider.style.display=""; 

    biasNone.classList.remove("active");
    biasDown.classList.add("active");
    biasUp.classList.remove("active");
    biasLeft.classList.remove("active");
    biasRight.classList.remove("active");

    console.log(`p_list = ${p_list}, direction = ${drn_map[direction]}, strength = ${delta}`) 
});

const biasSlider = document.getElementById("biasSlider"); 
biasSlider.style.display = "none";
biasSlider.addEventListener("input", () => {    
    delta = parseFloat(biasSlider.value);
    p_list = addBias(direction, delta);
    console.log(`p_list = ${p_list}, direction = ${drn_map[direction]}, strength = ${delta}`) 
});

// ====================================================================== //
// Reset button
function reset() {
    ctx_cluster.clearRect(0, 0, canvas_cluster.width, canvas_cluster.height);
    ctx_path.clearRect(0, 0, canvas_path.width, canvas_path.height);

    pauseButton.classList.remove("active");

    x = 0;
    y = 0;
    cluster = new Set();
    cluster.add(`${x},${y}`);

    counter = 0;
    stuck_counter = 0;
    R_max = 0;
}

bindButton( "resetButton", () => {
    reset();
    running = true;
    pauseButton.textContent = "Pause";
})
// ====================================================================== //
// Show walkers
// let prevDrawX, prevDrawY;
let show_walkers = false;

bindButton("showWalker", () => {
    show_walkers = !show_walkers;
    showWalker.classList.toggle("active");
    showWalker.textContent = show_walkers ? "Hide Particle Paths" : "Show Particle Paths";
    canvas_path.style.display = show_walkers ? "" : "none";
});

// ====================================================================== //
// Counter
let counter = 0;                            // No. of particles
let stuck_counter = 0;                      // No. of particles that stick
let ratio = (stuck_counter / counter) * 100;  // % of particles that stick

let N = document.getElementById("N");
N.textContent = counter;

let NStuck = document.getElementById("NStuck");
NStuck.textContent = stuck_counter;

let Ratio = document.getElementById("Ratio");
Ratio.textContent = ratio;

// ====================================================================== //
// Starting cluster
let cluster = new Set();
cluster.add(`${x},${y}`);

// Function to walk the particle
function stepParticle(x, y, p_list) {
    let node_list = [];

    // Make rolling list of probabilities
    for (let i = 0; i < p_list.length; i++) {
        if (i == 0) {
            node_list.push(p_list[i]); // If first element, add first element
        }
        else {
            node_list.push(p_list[i] + node_list[i-1]); // Else add current element plus last rolling element
        }
        
    }
    // Generate random number, and whichever is closest is the probability we go with
    const randomNum = Math.random();
    const probAtNode = (node_val) => randomNum < node_val; // test function
    // Prob. of being at some node = within what interval of nodes the roll lands

    let dirIndex = node_list.findIndex(probAtNode); // returns 0-3
    let [dx, dy] = nn_list[dirIndex];

    return {x: x+dx, y: y+dy} // Returns class-like thing
}

function spawnWalker(R_max) {
    let r = R_max + 5;
    const theta = 2*Math.PI * Math.random();
    let x = Math.round(r * Math.cos(theta));
    let y = Math.round(r * Math.sin(theta));

    return {x: x, y: y};
}

function isStuck(cluster, x, y, Pnn, Psnn) {
    let nn = [];
    let snn = [];

    // Adding each direction to the lists
    for (let i = 0; i < 4; i++) {
        nn.push({offset: nn_list[i], prob: Pnn});
        snn.push({offset: snn_list[i], prob: Psnn});
    }
    let neighbours = nn.concat(snn); // [nearest, second-nearest]

    // Looping through neighbours
    for (let {offset, prob} of neighbours) {
        let [dx, dy] = offset;
        if (cluster.has(`${x+dx},${y+dy}`)) { // If the coordinate to be moved to is in cluster, roll to stick
            let roll = Math.random()
            if (roll < prob) {
                return true;
            }
            else {
                continue;
            }
        }
    }
    return false;
}

function isDead(x, y, R_max) {
    let dist_sq = x**2 + y**2;
    let kill_rad_sq = Math.max(3*R_max, 8)**2;

    return dist_sq >= kill_rad_sq; /// boolean
}

// Animates an object so it moves in a random direction; includes walk via stepParticle
function animate() {
    // 1. Step walker /
    // 2. Check isStuck; if true, add to cluster and update R_max
    // 3. Else, check isDead; if true, discard and spawn new walker
    // 4. Else, continue!

    // Loop through, so each frame takes some amount of steps
    if (running) {
        for (let i = 0; i < STEPS_PER_FRAME; i++) {
            // Called like an object
            let result = stepParticle(x, y, p_list);
            x = result.x;
            y = result.y;
            
            ctx_path.fillRect(x+canvas_path.width/2, y+canvas_path.height/2, 2, 2);

            // Condition for sticking
            if (isStuck(cluster, x, y, Pnn, Psnn)) {
                cluster.add(`${x},${y}`);
                ctx_path.clearRect(0, 0, canvas_path.width, canvas_path.height);
                
                // Increment and update counters
                counter++;
                stuck_counter++;

                N.textContent = counter;
                NStuck.textContent = stuck_counter;

                // Drawing cluster
                // ctx_cluster.fillStyle = "rgb(0, 157, 175)";
                ctx_cluster.fillStyle = "rgb(252, 239, 60)";
                ctx_cluster.fillRect(x+canvas_cluster.width/2, y+canvas_cluster.height/2, 2, 2);

                // Take whatever R_max is bigger between the current value and the new cluster particle
                R_max = Math.max(R_max, Math.sqrt((x**2 + y**2)));
                result = spawnWalker(R_max);
                x = result.x;
                y = result.y;
            }

            // Particle kill condition
            else if (isDead(x, y, R_max)) {
                result = spawnWalker(R_max);
                x = result.x;
                y = result.y;  
                ctx_path.clearRect(0, 0, canvas_path.width, canvas_path.height);

                counter++;
                N.textContent = counter;
            }
        }    

    ratio = ((stuck_counter/counter) * 100).toFixed(2);
    Ratio.textContent = ratio;

    }   

    requestAnimationFrame(animate);
}
animate();