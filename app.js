'use strict';


var app = new Vue({
  el: "#app",
  data: {
    // Non-linkable state
    debug: false,
    minimap_modal: false,
    detail_id: 0,
    // Link-encoded state
    crusade: "ivory",
    plan: [0],
  },
  computed: {
    permalink: function() {
      // This function must be kept in sync with the section of created()
      let params = new URLSearchParams("");
      params.set("c",this.crusade);
      params.set("p",this.plan.join('-'));
      return params.toString();
    },
    crusade_info: function() {
      return crusade_data.get(this.crusade);
    },
    nodes: function() {
      return crusade_data.get(this.crusade).nodes;
    },
    detail: function() {
      return this.nodes[this.detail_id];
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
  created: function() {
    // This section must be kept in sync with the permalink() computed function
    let url = window.location.search;
    let params = new URLSearchParams(url);
    let crusade = String(params.get("c")).toLowerCase();
    // Sanitize and set crusade
    if (Array.from(crusade_data.keys()).includes(crusade)) {
      this.crusade = crusade;
      // Sanitize and set plan
      let plan_string = params.get("p");
      if (plan_string) {
        let plan = plan_string.split('-').map(x=>parseInt(x,10));
        let uniques = Array.from(plan.reduce((acc,val)=>acc.has(val)?acc:acc.set(val,1), new Map()).keys());
        let n_missions = crusade_data.get(this.crusade).nodes.length;
        if (plan.length==uniques.length &&
            plan.length>=1 &&
            plan.length<=n_missions &&
            plan.every(x=>!isNaN(x))) {
          this.plan = plan;
        }
      } else {
        console.log("Invalid plan specified. Reverting to default.");
      }
    } else {
      console.log("Invalid crusade specified. Reverting to default.");
    }

    // Update the URL. If it was valid, nothing changes.
    this.update_url();

    // Set up the modal-escape keybind.
    document.addEventListener('keydown', this.hide_minimap);
  },
  watch: { // All link-encoded states need to be watched.
    crusade: function () { this.update_url(); },
    plan: function () { this.update_url(); }
  },
  destroyed: function() {
    // Tear down the modal-escape keybind.
    document.removeEventListener('keydown', this.hide_minimap);
  },
  methods: {
    current_url: function(event) {
      return window.location;
    },
    update_url: function() {
      window.history.replaceState(null, null, "?"+this.permalink);
    },
    reset_plan: function() {
      this.plan = [0];
      this.detail_id = 0;
    },
    show_minimap: function(event, id) {
      event.preventDefault();
      if (id==0) { // Never show the start node.
        return;
      }
      this.minimap_modal = true;
    },
    hide_minimap: function(event) {
      if (event) {
        if (event.code!="Escape") {
          return;
        } else {
          event.preventDefault();
        }
      }
      this.minimap_modal = false;
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
