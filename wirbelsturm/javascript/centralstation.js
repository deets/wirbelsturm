var CentralStation = Backbone.Model.extend(
    {
        initialize : function() {
            _.bindAll(this, "start", "dispatch", "error", "ajax_send",
                     "ajax_complete");
            if(this.get("endpoint") == null) {
                throw new Error("Now endpoint given!");
            }
        },

        /*
         * Initialize a centralstation connection to an endpoint
         */
        start : function() {
            var url = this.get("endpoint") + "/" + new Date().getTime();
            var lmid = this.get("latest_message_id");
            if(lmid !== null) {
                url = url + "?latest_message_id=" +lmid;
            }
            $.ajax(
                {
                    "url" :  url, 
                    "success" : this.dispatch,
                    "error" : this.error,
                    "dataType" : "json"
                }
            );
            if(this.get("state") != "running") {
                this.set({"state" : "running"});                
            }
        },

        /*
         * Dispatch incoming messages.
         * messages must have the form
         * 
         * {
         *   (messages : <list of messages>,)?
         *   latest_messageId : <lmid>
         * }
         */
        dispatch : function(data) {
            var self = this;
            if("messages" in data) {
                $.each(
                    data.messages, 
                    function(__, message) {
                        self.trigger(message.scope, message.operation, message.payload);
                    }
                );
            }
            var lmid = data.latest_message_id;
            if(lmid !== undefined) {
                this.set({"latest_message_id" : lmid});
            }
            self.start();
        },

        /*
         * 
         */
        error : function(xhr, status, error) {
            // in case of timeout, just re-start
            if(xhr.status == 504) {
                this.start();           
            } else {
                this.set({ "state" : "error"});
            }
        },

        defaults : {
            state : "new",
            endpoint : null,
            latest_message_id : null
        }
    }
);