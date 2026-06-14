if(
    !localStorage.getItem(
        "session_id"
    )
){
    localStorage.setItem(
        "session_id",
        crypto.randomUUID()
    );
}

const SUPABASE_URL =
"https://orvrjxgcohlzkjjotlkn.supabase.co/rest/v1/analytics_events";

const SUPABASE_KEY =
"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im9ydnJqeGdjb2hsemtqam90bGtuIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODEyOTkxNjksImV4cCI6MjA5Njg3NTE2OX0.Sms5dlMvGzxWZFrvjgS3IX0XI1SNesD8PepkQJMzB9A";

async function trackEvent(
    eventName,
    eventValue = "",
    userType = "TEST"
){

    try{

        await fetch(
            SUPABASE_URL,
            {
                method:"POST",
                headers:{
                    "apikey":SUPABASE_KEY,
                    "Authorization":"Bearer " + SUPABASE_KEY,
                    "Content-Type":"application/json",
                    "Prefer":"return=minimal"
                },
                body:JSON.stringify({

                    session_id:
                        localStorage.getItem(
                            "session_id"
                        ),

                    user_type:
                        userType,

                    event_name:
                        eventName,

                    event_value:
                        eventValue

                })
            }
        );

        console.log(
            "TRACKED",
            eventName,
            eventValue
        );

    }catch(error){

        console.error(
            "TRACK ERROR",
            error
        );

    }

}
