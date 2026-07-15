// Global variables
const canvas = document.getElementById("canvas");
const ctx = canvas.getContext("2d");
const STEPS_PER_FRAME = 10000;

// Other variables
let x = 0;
let y = 0;
let R_max = 0;
let Pnn = 1;
let Psnn = 0;
let cluster = new Set();
cluster.add(`${x},${y}`);
let nn_list = [[1,0],[-1,0],[0,1],[0,-1]];
let snn_list = [[1,1],[-1,1],[1,-1],[-1,-1]];

let prevDrawX, prevDrawY;

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
    for (let i = 0; i < STEPS_PER_FRAME; i++) {
        // Called like an object
        let result = stepParticle(x, y, [0.25, 0.25, 0.25, 0.25]);
        x = result.x;
        y = result.y;

        // Condition for sticking
        if (isStuck(cluster, x, y, Pnn, Psnn)) {
            cluster.add(`${x},${y}`);

            // Drawing cluster
            ctx.fillStyle = "rgb(0 200 0)";
            ctx.fillRect(x+canvas.width/2, y+canvas.height/2, 2, 2);

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
        }
    }    

    ctx.fillStyle = "rgb(200 0 0/10%)";

    // ctx.clearRect(prevDrawX+canvas.width/2, prevDrawY+canvas.height/2, 5, 5);
    ctx.fillRect(x+canvas.width/2, y+canvas.height/2, 5, 5);
    // prevDrawX = x;
    // prevDrawY = y;
    
    requestAnimationFrame(animate);
    

}
animate();