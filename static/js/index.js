// This will be the object that will contain the Vue attributes
// and be used to initialize it.
let app = {};

// set_add_status <-- jackie
// add_post <--  jimmy
// reset_form <-- jimmy
// delete_post <-- jackie


// Given an empty app object, initializes it filling its attributes,
// creates a Vue instance, and then initializes the Vue instance.
let init = (app) => {

    // This is the Vue data.
    app.data = {
        // Complete as you see fit.
        rows: [],
        // Form fields
        reviews_contents: "",
        reviews_property_address: "",
        reviews_score_overall: "",
        reviews_score_responsiveness: null,
        reviews_score_friendliness: null,
        // End form fields
        add_mode: false,
        can_delete: false,
    };

    app.enumerate = (a) => {
        // This adds an _idx field to each element of the array.
        let k = 0;
        a.map((e) => {e._idx = k++;});
        return a;
    };


    app.add_post = function(){
        axios.post(add_reviews_url,
            {
                reviews_contents: app.vue.reviews_contents,
                //reviews_score_overall: app.vue.reviews_score_overall,
                reviews_score_responsiveness: app.vue.reviews_score_responsiveness,
                reviews_score_friendliness: app.vue.reviews_score_friendliness,
                reviews_property_address: app.vue.reviews_property_address

            }).then(function (response) {
            app.vue.rows.push({
                id: response.data.id,
                content: app.vue.reviews_contents,
                prop_address: app.vue.reviews_property_address,
                //score_overall: app.vue.reviews_score_overall,
                score_responsiveness: app.vue.reviews_score_responsiveness,
                score_friendliness: app.vue.reviews_score_friendliness,
            });
            app.enumerate(app.vue.rows);
            app.reset_form();
            //app.set_add_status(false);
        });
    };


    app.reset_form = function (){
        app.vue.add_content = "";
    };

    


    // This contains all the methods.
    app.methods = {
        // Complete as you see fit.
        add_post: app.add_post,
        reset_form: app.reset_form,
       
    };

    // This creates the Vue instance.
    app.vue = new Vue({
        el: "#vue-target",
        data: app.data,
        methods: app.methods
    });

    // And this initializes it.
    app.init = () => {
        // Put here any initialization code.
        // Typically this is a server GET call to load the data.
        axios.get(load_reviews_url).then(function (response) {
            app.vue.rows = app.enumerate(response.data.rows);
        });
    };

    // Call to the initializer.
    app.init();
};

// This takes the (empty) app object, and initializes it,
// putting all the code i
init(app);
