const dates   = document.getElementsByClassName('date');
const header  = document.getElementById('header');
const nav     = document.getElementById('nav');
const logo    = document.getElementById('logo');
const form    = document.getElementById('comment_form');
const comflow = document.getElementById('comflow');



// CONVERT epoch dates to date strings
function convertEpoch(dates) {
    for (const d of dates) {
        const opt = { dateStyle: "medium" };
        dt = parseInt(d.innerHTML);
        dt = new Date(dt * 1000);
        d.innerHTML = dt.toLocaleString('fr-FR', opt );
    }
}


convertEpoch(dates); // Convert post dates 


// The Header Scroll effect
window.addEventListener("scroll", (event) => {
    let scpos = this.scrollY;
    if (scpos > 100) {
        header.style.fontSize = '1em';
        nav.style.padding     = '.3em 0 .4em';
        logo.style.display    = 'none';
    } else {
        header.style.fontSize = null;
        nav.style.padding     = null;
        logo.style.display    = null;
    }
});



// Comment ajax processing
form.addEventListener('submit', function (e) {
    e.preventDefault();

    // Create new ajax request
    const xhr = new XMLHttpRequest();
    xhr.open('POST', '/comment', true);
    let comment = new FormData(form);
    xhr.send(comment);

    xhr.onreadystatechange = function() {
        comflow.innerHTML = '<h2 id="comtitle">Loading comments...</h2>';

        if(xhr.readyState === 4 && xhr.status === 200) {
            // responseText = returned by /comment route = all comments
            comflow.innerHTML = xhr.responseText;
            convertEpoch(comflow.getElementsByClassName('date'));
            form.reset();
        }
    }
});