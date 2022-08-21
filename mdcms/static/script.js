// Global
const doc     = document;
const dates   = doc.querySelectorAll('time');
const header  = doc.querySelector('#header');
const nav     = doc.querySelector('#nav');
// const logo    = doc.querySelector('#logo');

// /post
const comms   = doc.querySelector('#comments');
const comflow = doc.querySelector('#comflow');
const comform = doc.querySelector('#comform');
const form    = doc.querySelector('#comment_form');
const like    = doc.querySelector('#like');
const likcnt  = doc.querySelector('#likecounter');

// /posts
const pstlsts = doc.querySelectorAll('ul.postlist');
const catlist = doc.querySelector('ul#catlist');



// If in /posts
if (catlist && pstlsts) {
    let selectedCat = 'All';
    let postLis;            // A post <li>
    let pLis = new Array(); // All posts <li>
    let cats = new Array(); // All cats <li>
    let pdc;                // Post data-category attr value

    /*
    BUILD CATEGORY ARRAY from the
    "data-categories" <li> attribute in #postlist
    */

    // GET POSTS <li> in an array
    for (const postUl of pstlsts) {
        postLis = postUl.querySelectorAll('li');

        for (const postLi of postLis) {
            pLis.push(postLi);
        }
    }

    // BUILD CATEGORY LIST from data-categories attributes
    for (const pli of pLis) {
        pdc = pli.getAttribute('data-categories');

        if (pdc.length < 1) pli.setAttribute('data-categories', 'None');

        for (let cat of pdc.split(' ')) {
            if (cat.length < 1) cat = 'None';
            if (!cats.includes(cat)) cats.push(cat);        // cats == all categories
        }

    }

    // Create and append categories LIs
    for (let cat of cats) {
        let li = doc.createElement('li');
        li.innerHTML = cat;
        catlist.appendChild(li);
    }


    /*
    CATEGORY filtering
    */
    catlist.addEventListener('click', (e) => {
        if (e.target && e.target.matches('li')) {

            // Clic on already selected cat = reset
            if (selectedCat === e.target.innerHTML) selectedCat = 'All';
            else selectedCat = e.target.innerHTML;

            let reset = (selectedCat === 'All') ? true : false;

            // Selected category styling
            for (const cat of catlist.querySelectorAll('li')) {
                if (selectedCat === cat.innerHTML) {
                    cat.style.color = '#54c9b9';
                }
                else {
                    cat.removeAttribute('style');
                }
            }

            // Years H2 titles show/hide
            const h2year = doc.querySelectorAll('.titleyear');
            for (const h2 of h2year) {
                if (reset) {
                    h2.removeAttribute('style');
                }
                else {
                    h2.style.display = 'none';
                }
            }

            // Posts LI show/hide
            for (const postLi of pLis) {
                let postCats = postLi.getAttribute('data-categories').split(' ');
                                
                if (reset) {
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
        d.innerHTML = dt.toLocaleString('fr-FR', opt);
    }
}

convertEpoch(dates); // Convert post dates



/*
NAV scroll effect
*/
window.addEventListener('scroll', (e) => {
    let scpos = this.scrollY;
    if (scpos > 150) {
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
COMMENT
*/
if (form) {
    form.addEventListener('submit', (e) => {
        e.preventDefault();
        const newcom = new FormData(form);

        // Front side inputs tests
        let err = false;    // Error flag

        for (var i of newcom.entries()) {
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

        // AJAX / Send comment
        const xhr = new XMLHttpRequest();
        xhr.open('POST', '/comment');
        xhr.send(newcom);

        let currcom = comflow.innerHTML;

        xhr.onreadystatechange = () => {
            comflow.innerHTML = '<h2 id="comtitle">Loading comments...</h2>';

            if(xhr.readyState === 4) {
                switch (xhr.status) {
                    case 200:
                        // responseText = returned by /comment
                        // route = all comments
                        comflow.innerHTML = xhr.responseText;
                        convertEpoch(comflow.querySelectorAll('time'));
                        form.reset();
                        break;

                    case 403:
                        // ban
                        comflow.innerHTML = currcom;
                        comform.remove();
                        break;

                    default:
                        break;
                }
            }
        }
    });


    // TOGGLE SHOW/HIDE comment form (transition effect in CSS)
    var formstyle = window.getComputedStyle(form);
    var formheight = formstyle.getPropertyValue('height');
    form.style.height = '0px';

    doc.querySelector('#toggleform').addEventListener('click', (e) => {
        if (formstyle.getPropertyValue('height') < '1px') {


            window.scrollTo(form.getBoundingClientRect().x + 400,
                            form.getBoundingClientRect().y + 400);

            form.style.height = formheight;
            
        } else {
            form.style.height = '0px';
        }
    });
}



/*
LIKE
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

    like.addEventListener('mouseover', (e) => {
        liketop = (like.getBoundingClientRect().top - 50) + 'px';
        likeleft = (like.getBoundingClientRect().left -50) + 'px';

        let box = doc.createElement('div');
        box.setAttribute('id', 'likbox');
        box.setAttribute('class', 'msgbox');
        box.innerHTML = 'Like this page !';
        box.style.top = liketop;
        box.style.left = likeleft;
        doc.querySelector('body').appendChild(box);
    });

    like.addEventListener('mouseout', (e) => {
        doc.querySelector('#likbox').remove();
    });
}