// This will be the object that will contain the Vue attributes
// and be used to initialize it.
let app = {};

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
        reviews_score_responsiveness: "5",
        reviews_score_friendliness: "5",
        // End form fields
        add_mode: false,
        can_delete: false,
        count: 0,
    };

    app.enumerate = (a) => {
        // This adds an _idx field to each element of the array.
        let k = 0;
        a.map((e) => {e._idx = k++;});
        return a;
    };


    app.complete = (reviews) => {
        reviews.map((review) => {
            review.voted = 0;
            review.vote_display = 0;
        })
    };


    app.delete_post = function(row_idx){
        let id = app.vue.rows[row_idx].id;
        axios.get(delete_reviews_url, {params: {id: id}}).then(function(response){
            for(let i=0; i<app.vue.rows.length; i++){
                if(app.vue.rows[i].id == id){
                    app.vue.rows.splice(i, 1);
                    app.enumerate(app.vue.rows);
                    break;
                }
            }
        });
    }



    app.votes_hover = function(review_idx, vote_status){
        let review = app.vue.rows[review_idx];
        review.vote_display = vote_status;

        axios.get(get_voters_url, {params: {review_id: review.id}})
        .then((response) => {
            count = response.data.count;
            Vue.set(review, 'count', count);
        });
    };


    app.set_votes = function(review_idx, vote_status){
        let review = app.vue.rows[review_idx];

        if(vote_status !== review.voted){
            review.voted = vote_status;
        }
        else{
            review.voted = 0;
        }

        axios.post(set_votes_url, {review_id: review.id, voted: review.voted});
        axios.get(get_voters_url, {params: {review_id: review.id}})
        .then((response) => {
            count = response.data.count;
            Vue.set(review, 'count', count);
        });

    };


    app.load_count = function(review){
        axios.get(get_voters_url, {params: {review_id: review.id}})
        .then((response) => {
            count = response.data.count;
            Vue.set(review, 'count', count);
        });
    }



    // This contains all the methods.
    app.methods = {
        // Complete as you see fit.
        delete_post: app.delete_post,

        votes_hover: app.votes_hover,
        set_votes: app.set_votes,
        load_count: app.load_count
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
            let r = app.enumerate(response.data.rows);
            app.enumerate(r);
            app.complete(r);
            app.vue.rows = r;
        })
        .then(() => {
            for(let review of app.vue.rows) {
                app.load_count(review);
                axios.get(get_votes_url, {params: {"review_id": review.id}})
                    .then((result) => {
                        review.voted = result.data.voted;
                        review.vote_display = result.data.voted;
                    });
            }
        });
        
    };

    // Call to the initializer.
    app.init();
};

// This takes the (empty) app object, and initializes it,
// putting all the code i
init(app);
