<?php
session_start();
//echo basename($_SERVER['PHP_SELF']);
//require_once('req.php');
?>
<?php 
    $user = pg_escape_string($_SESSION['user']);
    //$curPageName = substr($_SERVER["SCRIPT_NAME"],strrpos($_SERVER["SCRIPT_NAME"],"/")+1);  
    //echo "The current page name is: ".$curPageName;  
    //echo "</br>";
    //echo $_SERVER['HTTP_REFERER'];  
?>


<!--body id="page-top" onLoad="$('#myModal').modal('show');"-->


<!-- body id="page-top" -->

    <!-- Navigation-->
    <nav class="navbar navbar-expand-lg navbar-light fixed-top py-3" id="mainNav">
            <div class="container">
                <a class="navbar-brand js-scroll-trigger" href="./index.php#page-top">Home</a>
                <button class="navbar-toggler navbar-toggler-right" type="button" data-toggle="collapse" data-target="#navbarResponsive" aria-controls="navbarResponsive" aria-expanded="false" aria-label="Toggle navigation"><span class="navbar-toggler-icon"></span></button>
                <div class="collapse navbar-collapse" id="navbarResponsive">
                    <ul class="navbar-nav ml-auto my-2 my-lg-0">
                        <li class="nav-item"><a class="nav-link js-scroll-trigger" href="./index.php#about">Come funziona</a></li>
                        <li class="nav-item"><a class="nav-link js-scroll-trigger" href="#contact">Contatti</a></li>
                    </ul>
                </div>
            </div>
        </nav>
<!--/html-->
