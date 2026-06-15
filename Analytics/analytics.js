alert("ANALYTICS V1");

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

    const response =
        await fetch(
            API_URL,
            {
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

    alert(
        "STATUS " +
        response.status
    );
}
