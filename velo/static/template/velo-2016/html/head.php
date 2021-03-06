<!DOCTYPE html>
<html lang="lv">
<head>
    <meta charset="UTF-8">
    <title>VELO.LV</title>
    <meta name="viewport" content="width=device-width, initial-scale=1, user-scalable=0">
    <meta http-equiv="X-UA-Compatible" content="IE=Edge">
    <meta name="format-detection" content="telephone=no">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="mobile-web-app-capable" content="yes">
    <meta name="SKYPE_TOOLBAR" content="SKYPE_TOOLBAR_PARSER_COMPATIBLE">
    
    <link rel="stylesheet" href="/css/main/main.css">
    
    <link rel="preload" href="/fonts/titillium/subset-TitilliumWeb-Bold.woff2" as="font" type="font/woff2" crossorigin>
    <link rel="preload" href="/fonts/titillium/subset-TitilliumWeb-Regular.woff2" as="font" type="font/woff2" crossorigin>
    <script>
        //image fades in when loaded
        function imgLoaded(img){
            var imgWrapper = img.parentNode;
            imgWrapper.className += imgWrapper.className ? ' loaded' : 'loaded';
        }; 
    </script> 
    <noscript>
    <style> 
        .img-wrapper img{
            opacity:1;
        }     
    </style>
    </noscript>
    
    <link rel="apple-touch-icon" sizes="57x57" href="/img/favicons/apple-touch-icon-57x57.png">
    <link rel="apple-touch-icon" sizes="60x60" href="/img/favicons/apple-touch-icon-60x60.png">
    <link rel="apple-touch-icon" sizes="72x72" href="/img/favicons/apple-touch-icon-72x72.png">
    <link rel="apple-touch-icon" sizes="76x76" href="/img/favicons/apple-touch-icon-76x76.png">
    <link rel="apple-touch-icon" sizes="114x114" href="/img/favicons/apple-touch-icon-114x114.png">
    <link rel="apple-touch-icon" sizes="120x120" href="/img/favicons/apple-touch-icon-120x120.png">
    <link rel="apple-touch-icon" sizes="144x144" href="/img/favicons/apple-touch-icon-144x144.png">
    <link rel="apple-touch-icon" sizes="152x152" href="/img/favicons/apple-touch-icon-152x152.png">
    <link rel="apple-touch-icon" sizes="180x180" href="/img/favicons/apple-touch-icon-180x180.png">
    <link rel="icon" type="image/png" href="/img/favicons/favicon-32x32.png" sizes="32x32">
    <link rel="icon" type="image/png" href="/img/favicons/favicon-194x194.png" sizes="194x194">
    <link rel="icon" type="image/png" href="/img/favicons/favicon-96x96.png" sizes="96x96">
    <link rel="icon" type="image/png" href="/img/favicons/android-chrome-192x192.png" sizes="192x192">
    <link rel="icon" type="image/png" href="/img/favicons/favicon-16x16.png" sizes="16x16">
    <link rel="manifest" href="/img/favicons/manifest.json">
    <link rel="mask-icon" href="/img/favicons/safari-pinned-tab.svg" color="#1a2126">
    <meta name="msapplication-TileColor" content="#da532c">
    <meta name="msapplication-TileImage" content="/img/favicons/mstile-144x144.png">
    <meta name="theme-color" content="#1a2126">
</head>
<body>
<div class="background">
    <figure class="background__image img-wrapper">
        <img
            data-src="/img/background-images/bg1.jpg"
            onload="imgLoaded(this)"
        >
        <div class="background__gradient"></div>
    </figure>
    
</div>
<div class="site">
<header class="main-header border-bottom">
    <div class="inner">
        <div class="main-header__inner w100 h100 border-left flex wrap--nowrap direction--row justify--start align-items--center">
            <div class="burger js-burger js-click-feedback">
                <div class="burger__bars">
                    <div class="burger-bar burger-bar--1"></div>
                    <div class="burger-bar burger-bar--2"></div>
                    <div class="burger-bar burger-bar--3"></div>
                </div>
            </div>
            <a href="sitemap.php" class="main-header__logo">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 76 15" width="76" height="15" enable-background="new 0 0 76 15"><g fill="#fff"><path d="M9.05,0.26h3.08L8.77,14.7H3.36L0,0.26h3.08l2.51,11.89h0.96L9.05,0.26z"/><path d="M14.25,14.7V0.26h9.34V2.8h-6.41v3.38h5.14v2.51h-5.14v3.46h6.41v2.55H14.25z"/><path d="M34.44,14.7h-8.22V0.26h2.93V12.1h5.29V14.7z"/><path d="m46.32 13.16c-.9 1.2-2.45 1.79-4.64 1.79s-3.74-.6-4.64-1.79c-.9-1.2-1.35-3.07-1.35-5.62s.45-4.44 1.35-5.68c.9-1.24 2.45-1.86 4.64-1.86s3.74.62 4.64 1.86c.9 1.24 1.35 3.13 1.35 5.68s-.45 4.42-1.35 5.62m-6.98-1.87c.42.74 1.2 1.11 2.35 1.11s1.93-.37 2.35-1.11c.42-.74.63-1.99.63-3.74s-.21-3.02-.64-3.81c-.42-.79-1.2-1.19-2.34-1.19s-1.91.4-2.34 1.19-.64 2.06-.64 3.81.21 2.99.63 3.74"/><path d="m50.01 14.7v-3.53h3.06v3.53h-3.06"/><path d="M64.26,14.7h-8.22V0.26h2.93V12.1h5.29V14.7z"/><path d="m72.92.26h3.08l-3.36 14.44h-5.41l-3.36-14.44h3.08l2.51 11.89h.96l2.5-11.89"/></g></svg>
            </a>
            <div class="mobile-nav flex--1 flex direction--row justify--end align-items--center">
                <form action="" method="POST" class="search order--1">
                    <label for="header-search" class="search__label js-placeholder">Meklēt</label>
                    <input type="text" id="header-search" name="search" class="search__input js-placeholder-up">
                    <button class="search__btn">
                        <svg class="icon">
                            <use xmlns:xlink="http://www.w3.org/1999/xlink" xlink:href="/img/icons.svg#search"></use>
                        </svg>
                    </button>
                </form>
                <nav class="main-nav flex--1">
                    <ul class="main-nav__items">
                        <li class="main-nav__item">
                            <a href="" class="main-nav__link">Kalendārs</a>
                        </li>
                        <li class="main-nav__item">
                            <a href="" class="main-nav__link">Rezultāti</a>
                        </li>
                        <li class="main-nav__item">
                            <a href="" class="main-nav__link">Galerijas</a>
                        </li>
                        <li class="main-nav__item">
                            <a href="" class="main-nav__link">Jaunumi</a>
                        </li>
                        <li class="main-nav__item">
                            <a href="" class="main-nav__link">Par mums</a>
                        </li>
                        <li class="main-nav__item">
                            <a href="" class="main-nav__link">Veikals</a>
                        </li>
                    </ul>
                </nav>
            </div>
            <div class="main-header__secondary-nav flex wrap--nowrap justify--end align-items--center">
                <!--a href="" class="login-link flex justify--center align-items--center">Ineākt</a-->
                <nav class="profile-nav js-profile-nav">
                    <div class="profile-nav__select flex direction--column justify--center align-items--center">
                        <figure class="profile-nav__hero flex justify--center align-items--center img-wrapper">
                            <img
                                class="profile-nav__hero-image"
                                data-src="/img/placeholders/velo-placeholder--1x1.svg"
                                onload="imgLoaded(this)"
                            >
                        </figure>
                        <div class="profile-nav__triangle"></div>
                    </div>
                    <ul class="profile-nav__items">
                        <li class="profile-nav__item">
                            <a href="" class="profile-nav__link">Par mani</a>
                        </li>
                        <li class="profile-nav__item">
                            <a href="" class="profile-nav__link">Sacensības</a>
                        </li>
                    </ul>
                </nav>
                
                <nav class="language-nav js-language-nav">
                    <div class="language-nav__selected">LV</div>
                    <ul class="language-nav__items">
                        <li class="language-nav__item">
                            <a href="" class="language-nav__link">RU</a>
                        </li>
                        <li class="language-nav__item">
                            <a href="" class="language-nav__link">EN</a>
                        </li>
                    </ul>
                </nav>
            </div>
        </div>
    </div>
</header>