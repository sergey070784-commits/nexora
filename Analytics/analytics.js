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
"https://lglxpwwccxzfacdtbcbp.supabase.co/rest/v1/analytics_events";

const SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImxnbHhwd3djY3h6ZmFjZHRiY2JwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODE1MDU3MTAsImV4cCI6MjA5NzA4MTcxMH0.ZI2CryDHE9w0WXPLA2E2GYZDFy5_tWlC6CICSzsPWa8";

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
