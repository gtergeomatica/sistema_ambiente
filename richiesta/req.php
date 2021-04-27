<?php 
$subtitle2=str_replace("'","\'",str_replace(' ','_',$subtitle));
?>

    




<!-- File CSS e fontawesome -->
<link rel="icon" type="image/x-icon" href="assets/img/favicon.ico" />
        <!-- Font Awesome icons (free version)-->
        <script src="fontawesome_free_5_15_2_web/js/all.js" crossorigin="anonymous"></script>
        <!-- Google fonts-->
        <link href="https://fonts.googleapis.com/css?family=Merriweather+Sans:400,700" rel="stylesheet" />
        <link href="https://fonts.googleapis.com/css?family=Merriweather:400,300,300italic,400italic,700,700italic" rel="stylesheet" type="text/css" />
        <!-- Third party plugin CSS-->
        <!--link href="https://cdnjs.cloudflare.com/ajax/libs/magnific-popup.js/1.1.0/magnific-popup.min.css" rel="stylesheet" /-->
        <link href="css/magnific-popup.min.css" rel="stylesheet" />
        <!-- Core theme CSS (includes Bootstrap)-->
        <link href="css/styles.css" rel="stylesheet" />
        <link href="leaflet/leaflet.css" rel="stylesheet" />
        <script src="leaflet/leaflet.js"></script>



<meta HTTP-EQUIV=keywords CONTENT="GIS hosting Sistema Ambiente"> 

    



    



 


    <!-- HTML5 Shim and Respond.js IE8 support of HTML5 elements and media queries -->
    <!-- WARNING: Respond.js doesn't work if you view the page via file:// -->
    <!--[if lt IE 9]>
        <script src="https://oss.maxcdn.com/libs/html5shiv/3.7.0/html5shiv.js"></script>
        <script src="https://oss.maxcdn.com/libs/respond.js/1.4.2/respond.min.js"></script>
    <![endif]-->
    <!-- Bootstrap Core CSS -->
    <!--link rel="stylesheet" href="./bootstrap/dist/css/bootstrap.min.css" type="text/css"-->
    
    <link href="bootstrap-select/dist/css/bootstrap-select.css" rel="stylesheet" />

    <!-- Bootstrap Table CSS -->
	<!--link rel="stylesheet" href="./bootstrap-table/dist/bootstrap-table.min.css" -->
	<!--link rel="stylesheet" href="./bootstrap-table/dist/extensions/export/bootstrap-table-export.css" -->
	<!--link rel="stylesheet" href="./bootstrap-table/dist/extensions/filter-control/bootstrap-table-filter-control.css" -->
	<!--link rel="stylesheet" href="./bootstrap-table/dist/extensions/print/bootstrap-table-print.min.css"-->
    <!-- Custom Fonts -->
    <!--link href='http://fonts.googleapis.com/css?family=Open+Sans:300italic,400italic,600italic,700italic,800italic,400,300,600,700,800' rel='stylesheet' type='text/css'>
    <link href='http://fonts.googleapis.com/css?family=Merriweather:400,300,300italic,400italic,700,700italic,900,900italic' rel='stylesheet' type='text/css'-->
    <!--link rel="stylesheet" href="font-awesome-4.5.0/css/font-awesome.min.css" type="text/css"-->

    <!-- Plugin CSS -->
    <!--link rel="stylesheet" href="css/animate.min.css" type="text/css"-->

    <!-- Custom CSS -->
    <!--link rel="stylesheet" href="css/creative.css" type="text/css"-->


    <!--link rel="stylesheet" href="./bootstrapvalidator-master/dist/css/bootstrapValidator.css"/-->


    <!-- HTML5 Shim and Respond.js IE8 support of HTML5 elements and media queries -->
    <!-- WARNING: Respond.js doesn't work if you view the page via file:// -->
    <!--[if lt IE 9]>
        <script src="https://oss.maxcdn.com/libs/html5shiv/3.7.0/html5shiv.js"></script>
        <script src="https://oss.maxcdn.com/libs/respond.js/1.4.2/respond.min.js"></script>
    <![endif]-->

<!-- Stili da sovrascrivere ad altri CSS -->
<style>
body{
    font-family: Arial, Helvetica, sans-serif;
}
table th, .table td {
    padding: 0.5rem;
}
/* Green check. */
.glyphicon-ok {
    color: green;
}
/* Red X. */
.glyphicon-remove {
    color: red;
}

/*.modal {
  display:block;
}*/
.navbar-nav li:hover > ul.dropdown-menu {
    display: block;
}
.dropdown-submenu {
    position: relative;
}

.dropdown-submenu .dropdown-menu {
    top: 0;    
    min-width: fit-content;
    left: 100%;
    margin-top: -1px;
}
.has-error label{
    color: yellow;
    border-color: yellow;
}
.has-error input,
.has-error textarea {
    /*color: yellow;*/
    background-color: yellow;
}
.mytip {
  position: relative;
  opacity: 1;
}
.tooltiptext {
  visibility: hidden;
  width: 150px;
  font-size: small;
  background-color: #555;
  color: #fff;
  text-align: center;
  border-radius: 6px;
  padding: 5px 0;
  position: absolute;
  z-index: 1;
  bottom: 125%;
  left: 50%;
  margin-left: -75px;
  opacity: 0;
  transition: opacity 0.3s;
}
.mytip .tooltiptext::after {
  content: "";
  position: absolute;
  top: 100%;
  left: 50%;
  margin-left: -5px;
  border-width: 5px;
  border-style: solid;
  border-color: #555 transparent transparent transparent;
}
.mytip:hover .tooltiptext {
  visibility: visible;
  opacity: 1;
}


.btn-link {
    border: none;
    outline: none;
    background: none;
    cursor: pointer;
    color: #0000EE;
    padding: 0;
    text-decoration: underline;
    font-family: inherit;
    font-size: inherit;
}

</style>


    <!-- HTML5 Shim and Respond.js IE8 support of HTML5 elements and media queries -->
    <!-- WARNING: Respond.js doesn't work if you view the page via file:// -->
    <!--[if lt IE 9]>
        <script src="https://oss.maxcdn.com/libs/html5shiv/3.7.0/html5shiv.js"></script>
        <script src="https://oss.maxcdn.com/libs/respond.js/1.4.2/respond.min.js"></script>
    <![endif]-->

<!-- <script> 
setTimeout(function() {
    $('#myModal').modal();
}, 10000);
</script> -->

<!-- jQuery -->
<script src="jquery/jquery-3.5.1.min.js"></script>
<!--script src="./jquery/dist/jquery.min.js"></script-->



<?php
// end
?>
    
