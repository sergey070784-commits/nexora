const SUPABASE_URL =
"https://orvrjxgcohlzkjjotlkn.supabase.co/rest/v1/analytics_events";

const SUPABASE_KEY =
"ВСТАВИ СВОЙ ANON KEY";

async function trackEvent(
    eventName,
    eventValue,
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
                    session_id:"demo_session",
                    user_type:userType,
                    event_name:eventName,
                    event_value:eventValue
                })
            }
        );

        console.log(
            "TRACKED:",
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
