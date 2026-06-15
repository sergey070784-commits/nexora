console.log("ANALYTICS LOADED");
if (!localStorage.getItem("session_id")) {
    localStorage.setItem(
        "session_id",
        crypto.randomUUID()
    );
}

const API_URL =
"https://sheetdb.io/api/v1/u0i9fpqemftro";

async function trackEvent(
    eventName,
    eventValue = "",
    page = ""
){

    try{

        const response =
            await fetch(
            API_URL,
            {
            console.log(
                "SHEETDB STATUS",
                response.status
                ); 
                method:"POST",
                headers:{
                    "Content-Type":
                    "application/json"
                },
                body:JSON.stringify({
                    data:[
                        {
                            session_id:
                                localStorage.getItem(
                                    "session_id"
                                ),

                            timestamp:
                                new Date()
                                .toISOString(),

                            event_name:
                                eventName,

                            event_value:
                                eventValue,

                            page:
                                page
                        }
                    ]
                })
            }
        );

        console.log(
            "TRACKED",
            eventName
        );

    }catch(error){

        console.error(
            error
        );

    }

}
