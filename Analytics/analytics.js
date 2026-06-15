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

const SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im9ydnJqeGdjb2hsemtqam90bGtuIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc4MTI5OTE2OSwiZXhwIjoyMDk2ODc1MTY5fQ.e7K8svoztu49w-rk0Byos67xPC1Fz7XutuOtjn5C8Kg";

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

                    channel:
                        "WEB",

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
