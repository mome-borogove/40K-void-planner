'use strict';


var app = new Vue({
  el: "#app",
  data: {
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
    }
  },
  methods: {
    toggle_node: function(id) {
      if (id==0) { // Never toggle the start node.
        return;
      }
      if (!this.plan.includes(id)) { // Try to add to plan
        if (this.is_one_adjacent_enabled(this.nodes[id], this.plan)) {
          this.plan.push(id);
        } else {
          console.log('No connection to node '+String(id));
        }
      } else { // Try to remove from plan
        // Check if removing the node will disable further nodes in the plan
        let plan_without_current = Array.from(this.plan);
        plan_without_current.splice(this.plan.indexOf(id),1);
        let satisfied = plan_without_current.map((order,idx) =>
          order<0 || this.is_one_adjacent_enabled(this.nodes[idx], plan_without_current) );
        console.log('Satisfied: '+String(satisfied));
        if (!satisfied.every(e=>e)) {
          console.log('NOT SATISFIED: '+String(satisfied.map(e=>e)));
          return;
        }
        // Okay, let's remove it.
        console.log('Trying to remove '+id);
        this.plan.splice(this.plan.indexOf(id),1);
        // Move all subsequent plan nodes up one place in the plan
      }
    },
    planned_difficulty: function(id) {
      return null;
    },
    is_one_adjacent_enabled: function(self, enabled_array) {
      console.log('Is one adjacent enabled?');
      console.log(self.id);
      console.log(self.deps);
      return true;
      // Use De Morgan's to get around Javascript's empty array behavior
      return !(self.deps.every(idx => !enabled_array.includes(idx)));
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
      console.log(s);
      console.log(s.slice(0,1));
      console.log(s.slice(0,1).toUpperCase);
      return s.slice(0,1).toUpperCase() + s.slice(1);
    }
  }
})
