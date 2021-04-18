const dates   = document.getElementsByClassName('date');
const header  = document.getElementById('header');
const nav     = document.getElementById('nav');
const logo    = document.getElementById('logo');
const form    = document.getElementById('comment_form');
const comflow = document.getElementById('comflow');
const like    = document.getElementById('like');
const likcnt  = document.getElementById('likecounter');



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
window.addEventListener("scroll", (e) => {
    let scpos = this.scrollY;
    if (scpos > 100) {
        header.style.fontSize = '1em';
        nav.style.padding     = '.3em 0 .4em';
        logo.style.display    = 'none';
        like.style.opacity    = .5;
    } else {
        header.style = null;
        nav.style    = null;
        logo.style   = null;
        like.style   = null;
    }
});



// Like btn
like.addEventListener('click', (e) => {
    const xhr = new XMLHttpRequest();
    xhr.open('POST', '/like');
    xhr.send();

    xhr.onreadystatechange = () => {
        if (xhr.readyState === 4 && xhr.status === 200) {
            likcnt.innerHTML = xhr.responseText;
        }
    }
})



// When clicking comment Submit btn
// Form tests + ajax processing
form.addEventListener('submit', (e) => {
    e.preventDefault();
    const newcom = new FormData(form);
    let err = false;    // Error flag

    // Inputs test
    for(var i of newcom.entries()){
        let ele = document.getElementById(i[0]);
        let len = i[1].length;
        ele.style = null;

        switch (i[0]) {
            // NAME must be 2-20 chars
            case 'name':
                if (len < 2 || len > 20) {
                    ele.style.backgroundColor= '#bd9191';
                    err = true;
                }
                break;

            // EMAIL must be 0 (blank), or > 7 chars
            // TODO : regex test
            case 'email':
                if (len > 0 && len < 8) {
                    ele.style.backgroundColor= '#bd9191';
                    err = true;
                }
                break;
            
            // COMMENT must be 6-1000 chars
            case 'comment':
                if (len < 6 || len > 1000) {
                    ele.style.backgroundColor= '#bd9191';
                    err = true;
                }
                break;
        }
    }

    if (err)
        return; // If any error, do not process request

    // Save  current comment flow
    const currcom = comflow.innerHTML;

    // TODO CALL CAPTCHA

    // SEND COMMENT
    // Create new ajax request
    const xhr = new XMLHttpRequest();
    xhr.open('POST', '/comment');
    xhr.send(newcom);

    xhr.onreadystatechange = () => {
        comflow.innerHTML = '<h2 id="comtitle">Loading comments...</h2>';
        
        if(xhr.readyState === 4) {
            switch (xhr.status) {
                case 403:
                    // Do nothing, restore comment flow
                    comflow.innerHTML = currcom;
                    break;

                case 200:
                    // responseText = returned by /comment route = all comments
                    comflow.innerHTML = xhr.responseText;
                    convertEpoch(comflow.getElementsByClassName('date'));
                    form.reset();
                    break;

                default:
                    break;
            }
        }
    }
});