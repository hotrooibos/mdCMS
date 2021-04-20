// Global
const dates   = document.getElementsByTagName('time');
const header  = document.getElementById('header');
const nav     = document.getElementById('nav');
// const logo    = document.getElementById('logo');

// /post
const form    = document.getElementById('comment_form');
const comflow = document.getElementById('comflow');
const like    = document.getElementById('like');
const likcnt  = document.getElementById('likecounter');

// /posts
const pstlist = document.getElementById('postlist');
const categs  = document.getElementById('categories');



// If in /posts
if (categs && pstlist) {

    /*
    BUILD CATEGORY ARRAY from the
    "data-categories" <li> attribute in #postlist
    */
    const plis = pstlist.getElementsByTagName('li');
    let cats = new Array();

    // Build category list from data-categories attributes
    for (const pli of plis) {
        let c = pli.getAttribute('data-categories');
        for (const cat of c.split(' ')) {
            if (!cats.includes(cat)) cats.push(cat);
        }
    }
    // Create <li> list of categories
    for (const cat of cats) {
        let li = document.createElement("li");
        li.innerHTML = cat;
        li.setAttribute('data-state', 'disabled');
        categs.insertBefore(li, categs.firstChild);
    }



    /*
    CATEGORY FILTERING
    */
    categs.addEventListener('click', (e) => {
        if (e.target && e.target.matches('li')) {
            const clis = categs.getElementsByTagName('li');
            let filters = new Array();

            // Btn All
            if (e.target.innerHTML === 'All') {
                filters.length = 0; // Clear array
                for (const cli of clis) {
                    cli.setAttribute('data-state', 'disabled');
                }
            }

            let state = e.target.getAttribute('data-state');

            // Change li state
            if (state === 'enabled') {
                e.target.setAttribute('data-state', 'disabled');
            }
            else {
                e.target.setAttribute('data-state', 'enabled');
            }

            // Filter/refresh post list
            for (const cli of clis) {
                let state = cli.getAttribute('data-state');
                if (state === 'enabled') filters.push(cli.innerHTML);
            }
  
            for (const pli of plis) {
                let cats = pli.getAttribute('data-categories').split(' ');
                
                if (filters.length !== 0) {
                    for (const cat of cats) {
                        
                        if (!filters.includes(cat)) {
                            pli.style.display = 'none';
                        }
                        else {
                            pli.style = null;
                            break;
                        }
                    }
                }
                else {
                    pli.style = null;
                }
            }
        }
    });
}



/*
CONVERT EPOCH time to datetime
*/
function convertEpoch(dates) {
    for (const d of dates) {
        const opt = { dateStyle: "medium" };
        dt = parseInt(d.innerHTML);
        dt = new Date(dt * 1000);
        d.innerHTML = dt.toLocaleString('fr-FR', opt );
    }
}

convertEpoch(dates); // Convert post dates 



/*
The Header SCROLL EFFECT
*/
window.addEventListener("scroll", (e) => {
    let scpos = this.scrollY;
    if (scpos > 100) {
        header.style.fontSize = '1em';
        nav.style.padding = '.3em 0 .4em';
        // logo.style.display = 'none';
        if (like) like.style.opacity = .5;
    } else {
        header.style = null;
        nav.style = null;
        // logo.style = null;
        if (like) like.style = null;
    }
});



/*
LIKE btn
*/
if (like) {
    like.addEventListener('click', (e) => {
        const xhr = new XMLHttpRequest();
        xhr.open('POST', '/like');
        xhr.send();

        xhr.onreadystatechange = () => {
            if (xhr.readyState === 4 && xhr.status === 200) {
                likcnt.innerHTML = xhr.responseText;
            }
        }
    });
}



/*
SUBMIT COMMENT ajax processing
*/
if (form) {
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
                        // responseText = returned by /comment
                        // route = all comments
                        comflow.innerHTML = xhr.responseText;
                        convertEpoch(comflow.getElementsByTagName('time'));
                        form.reset();
                        break;

                    default:
                        break;
                }
            }
        }
    });
}