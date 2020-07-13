'use strict';


var app = new Vue({
  el: "#app",
  data: {
    debug: false,
    crusade: "ivory",
    plan: [0],
  },
  computed: {
    crusade_info: function() {
      return crusade_data.get(this.crusade);
    },
    nodes: function() {
      return crusade_data.get(this.crusade).nodes;
    },
    crusade_list: function() {
      return crusade_data;
    },
    current_difficulty: function() {
      return this.plan.reduce( (acc,id) => acc+this.nodes[id].difficulty, 0)
    },
    average_difficulty: function() {
      return this.plan.reduce( (acc,id) => acc+this.planned_difficulty(id) )/this.plan.length;
    }
  },
  methods: {
    reset_plan: function() {
      this.plan = [0];
    },
    toggle_node: function(id) {
      if (id==0) { // Never toggle the start node.
        return;
      }
      if (!this.plan.includes(id)) { // Try to add to plan
        if (this.connected(this.nodes[id])) {
          this.plan.push(id);
        } else {
          console.log('No connection to node '+String(id));
        }
      } else { // Try to remove from plan
        // Check if removing the node will disable further nodes in the plan
        let modified_plan = Array.from(this.plan);
        modified_plan.splice(this.plan.indexOf(id),1);
        // Now replay the plan and check for disconnections.
        let satisfied = true;
        for (let progress=1; progress<modified_plan.length; progress++) {
          let replay_plan = modified_plan.slice(0,progress);
          let replay_id = modified_plan[progress]
          //console.log('Checking node '+String(replay_id)+' against '+String(replay_plan));
          satisfied &= this.connected_using_plan(this.nodes[replay_id], replay_plan);
          if (!satisfied) {
            console.log('Not satisfied: node '+String(replay_id)+' would be disconnected');
            return;
          }
        }

        // Okay, let's remove it.
        this.plan.splice(this.plan.indexOf(id),1);
        // Move all subsequent plan nodes up one place in the plan
      }
    },
    connected: function(node) {
      return this.connected_using_plan(node, this.plan);
    },
    connected_using_plan: function(node, plan) {
      //console.log('Is '+String(node.id)+' connected? (deps: '+String(node.deps)+')');
      //console.log(plan);
      if (plan.includes(node.id)) {
        return true;
      }
      for (const step_id of plan) {
        if (node.deps.includes(step_id)) {
          return true;
        }
      }
      return false;
    },
    planned_difficulty: function(id) {
      let node = this.nodes[id];
      let current_difficulty = 0
      //console.log('Planned_difficulty('+String(id)+') with deps '+String(node.deps)+' and plan '+String(this.plan));
      for (const step_id of this.plan) {
        let step = this.nodes[step_id];
        //console.log('Considering step '+String(step.id)+' ('+String(step.name)+') with difficulty '+String(step.difficulty)+' and deps '+String(step.deps));
        if (step_id==id) { // Hey, it's us!
          return current_difficulty;
        }
        current_difficulty += step.difficulty;
        //console.log('Is adjacent?: '+String(node.deps.includes(step_id)));
        if (node.deps.includes(step_id)) {
          return current_difficulty;
        }
      }
      return -1;
    },
    y_correct: function(y) {
      // Y-axis units are in %, but for the trig, that's not going to work.
      // Instead, we need to account for the aspect ratio (which we've fixed).
      // All units are in X-axis units.
      return .5625*y; // 16:9 aspect ratio
    },
    angle: function(start_node, end_node) {
      let dx = end_node.x - start_node.x;
      let dy = this.y_correct(end_node.y - start_node.y); // Measured from top
      return Math.atan2(dy,dx);
      return angle
    },
    distance: function(start_node, end_node) {
      let dx = end_node.x - start_node.x;
      let dy = this.y_correct(end_node.y - start_node.y);
      //return Math.sqrt(dx*dx + dy*dy)/2;
      return Math.sqrt(dx*dx + dy*dy);
    },
    capitalize: function(s) {
      return s.slice(0,1).toUpperCase() + s.slice(1);
    }
  }
})
