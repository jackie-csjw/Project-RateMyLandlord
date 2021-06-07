// This will be the object that will contain the Vue attributes
// and be used to initialize it.
let app = {};


// Given an empty app object, initializes it filling its attributes,
// creates a Vue instance, and then initializes the Vue instance.
let init = (app) => {

    // This is the Vue data.
    app.data = {
        // Complete as you see fit.
        query: "",
        rows: [],
        not_found: null
    };

    app.enumerate = (a) => {
        // This adds an _idx field to each element of the array.
        let k = 0;
        a.map((e) => {e._idx = k++;});
        return a;
    };

    app.search = function () {
        if (app.vue.query.length > 1) {
            axios.get(search_url, {params: {q: app.vue.query}})
                .then(function (row) {
                    app.vue.rows = row.data.rows;
                    app.vue.not_found = row.data.not_found;
                });
        } else {
            app.vue.rows = [];
            app.vue.not_found = ''
        }
        
    };

    app.goto_lord = function (){
       

        for(let i = 0; i < app.vue.rows.length; i++){
            let l = app.vue.rows[i];
            axios.get(get_search_url_url, {params: {lord_id: l.id}})
            .then(function(r){
                console.log("here");
                window.location = r.data.url;
            });
        }
    };

    app.link_to = function () {
        
    }

    // This contains all the methods.
    app.methods = {
        // Complete as you see fit.
        search: app.search,
        goto_lord: app.goto_lord
       
    };

    // This creates the Vue instance.
    app.vue = new Vue({
        el: "#vue-target",
        data: app.data,
        methods: app.methods
    });

    // And this initializes it.
    app.init = () => {
    
    };

    // Call to the initializer.
    app.init();
};

// This takes the (empty) app object, and initializes it,
// putting all the code i
init(app);
