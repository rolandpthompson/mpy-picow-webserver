async function getPins() {
    let url = 'http://192.168.30.6/api/status';
    try {
        let res = await fetch(url, {method:'GET', headers: {'Authorization': 'Basic ' + btoa('user:pass')}});
        return await res.json();
    } catch (error) {
        console.log(error);
    }
}

async function renderPins() {
    let pins = await getPins();
    let html = '';
    pins.forEach(pin => {
        let htmlSegment = `<div class="Pin">
                            <h2>${pin.Name}</h2>
                            <div class="email">${pin.State}</div>
                        </div>`;

        html += htmlSegment;
    });

    let container = document.querySelector('.container');
    container.innerHTML = html;
}

renderPins();