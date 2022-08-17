async function getPins() {
    let url = 'http://192.168.30.6/api/status';
    try {
        //let res = await fetch(url, {method:'GET', headers: {'Authorization': 'Basic ' + btoa('un:pwd')}});
        let res = await fetch(url, {method:'GET', headers: { credentials: 'include' }});
        return await res.json();
    } catch (error) {
        console.log(error);
    }
}

async function renderPins() {
    let pins = await getPins();
    let html = '';
    pins.forEach(pin => {


        let stateText = 'Off';
        let toggleState = 'buttonOn';
        if (pin.State == 1) {
            stateText = 'On';
            toggleState = 'buttonOff';
        }

        let htmlSegment = `<div class="card">
                                <div class="container">
                                <h4><b>${pin.Name}</b></h4>
                                <p>Current state is: ${stateText}</p>
                                <button id="${pin.Relay}_TOGGLE" class="button ${toggleState}" onClick="button_click(${pin.Relay}, -1)">Toggle</button>
                                <button id="${pin.Relay}_ON" class="button buttonOn" onClick="button_click(${pin.Relay}, 1)">Force On</button>
                                <button id="${pin.Relay}_OFF" class="button buttonOff" onClick="button_click(${pin.Relay}, 0)">Force Off</button>
                                </div>
                           </div>`;

        html += htmlSegment;
    });

    let container = document.querySelector('.container');
    container.innerHTML = html;
}

function button_click(control, state)
{
    let url = 'http://192.168.30.6/api/';
    
    if (state == -1)
        url += 'toggle/RELAY' + control;
    else if (state == 0)
        url += 'disable/RELAY' + control;
    else if (state == 1)
        url += 'enable/RELAY' + control;

    fetch(url, {
        method: "POST",
        headers: { credentials: 'include' }
    }).then(() => {
        window.location.reload();
    })

}

renderPins();