import codecs

js = codecs.open('static/app.js', 'r', 'utf-8').read()

volume_code = '''
let previewVolume = 50;
let volHideTimeout;

function playOledVolume(delta) {
    previewVolume += delta * 5;
    if (previewVolume > 100) previewVolume = 100;
    if (previewVolume < 0) previewVolume = 0;

    const idle = document.getElementById('oled-idle');
    const layer = document.getElementById('oled-anim-layer');
    if(!idle || !layer) return;
    
    idle.style.display = 'none';
    layer.style.display = 'flex';
    layer.className = 'oled-anim-layer';
    
    layer.innerHTML = \<div style="width: 80%; text-align: center;">
        <div style="font-size: 10px; color: #fff; margin-bottom: 2px;">VOLUMEN</div>
        <div style="width: 100%; height: 10px; border: 1px solid #fff; border-radius: 2px; padding: 1px; box-sizing: border-box; display: flex; align-items: stretch;">
            <div style="width: \%; background: #fff; transition: width 0.1s;"></div>
        </div>
    </div>\;

    clearTimeout(volHideTimeout);
    volHideTimeout = setTimeout(() => {
        layer.style.display = 'none';
        idle.style.display = 'block';
    }, 1500);
}
'''

js = js.replace('function simulateAction(id)', volume_code + '\nfunction simulateAction(id)')

# Now inject into the drag handler
js = js.replace('simulateAction(-3); // Simulate giro', 'simulateAction(-3); // Simulate giro\n        playOledVolume(diff > 0 ? 1 : -1);')

codecs.open('static/app.js', 'w', 'utf-8').write(js)
