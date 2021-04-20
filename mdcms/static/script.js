// Global
const doc = document;
const dates   = doc.querySelectorAll('time');
const header  = doc.querySelector('#header');
const nav     = doc.querySelector('#nav');
// const logo    = doc.querySelector('#logo');

// /post
const form    = doc.querySelector('#comment_form');
const comflow = doc.querySelector('#comflow');
const like    = doc.querySelector('#like');
const likcnt  = doc.querySelector('#likecounter');

// /posts
const pstlsts = doc.querySelectorAll('.postlist');
const categs  = doc.querySelector('#catlist');



// If in /posts
if (categs && pstlsts) {

    /*
    BUILD CATEGORY ARRAY from the
    "data-categories" <li> attribute in #postlist
    */

    // GET POSTS <li> in an array
    let plis = new Array();                                 // plis == all posts <li>
    for (const post_ul of pstlsts) {
        let postLis = post_ul.querySelectorAll('li');

        for (const post_li of postLis) {
            plis.push(post_li);
        }
    }


    // BUILD CATEGORY LIST from data-categories attributes
    let cats = new Array();
    for (const pli of plis) {
        let c = pli.getAttribute('data-categories');

        if (c.length < 1) pli.setAttribute('data-categories', 'None');

        for (let cat of c.split(' ')) {
            if (cat.length < 1) cat = 'None';
            if (!cats.includes(cat)) cats.push(cat);        // cats == all categories
        }

    }

    for (let cat of cats) {
        let li = doc.createElement("li");
        li.innerHTML = cat;
        categs.appendChild(li);
    }


    /*
    CATEGORY FILTERING
    */
    categs.addEventListener('click', (e) => {
        if (e.target && e.target.matches('li')) {
            const selectedCat = e.target.innerHTML;
            
            for (const cat of categs.querySelectorAll('li')) {
                cat.removeAttribute('style');
            }
            e.target.style.color = '#54c9b9';

            for (const postLi of plis) {
                let postCats = postLi.getAttribute('data-categories').split(' ');
                
                if (selectedCat === 'All') {
                    postLi.removeAttribute('style');
                    continue;
                }

                if (!postCats.includes(selectedCat)) {
                    postLi.style.display = 'none';
                }
                else {
                    postLi.removeAttribute('style');
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
            let ele = doc.getElementById(i[0]);
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
                        convertEpoch(comflow.querySelectorAll('time'));
                        form.reset();
                        break;

                    default:
                        break;
                }
            }
        }
    });
}