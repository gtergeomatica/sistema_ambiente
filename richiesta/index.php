<?php
session_start();
$curPageName = substr($_SERVER["SCRIPT_NAME"],strrpos($_SERVER["SCRIPT_NAME"],"/")+1);
$user_admin="comuneisernia";
//$gruppo = 'comuneisernia3_group';
$cliente = 'Sistema Ambiente';
?>


<!DOCTYPE html>
<html lang="en">
    <head>
        <meta charset="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no" />
        <meta name="description" content="" />
        <meta name="author" content="" />
        <title>Sistema Istanze CDU del <?php echo $cliente; ?></title>
        <!-- Richiama stili e file css-->
        <?php
        require('req.php');
        ?>
    </head>
    <body id="page-top">
    <!-- Richiama la navbar-->
    <div id="navbar1">
<?php
require('navbar.php');
?>
</div>
        <!-- Navigation-->
        <!--nav class="navbar navbar-expand-lg navbar-light fixed-top py-3" id="mainNav">
            <div class="container">
                <a class="navbar-brand js-scroll-trigger" href="#page-top">Home</a>
                <button class="navbar-toggler navbar-toggler-right" type="button" data-toggle="collapse" data-target="#navbarResponsive" aria-controls="navbarResponsive" aria-expanded="false" aria-label="Toggle navigation"><span class="navbar-toggler-icon"></span></button>
                <div class="collapse navbar-collapse" id="navbarResponsive">
                    <ul class="navbar-nav ml-auto my-2 my-lg-0">
                        <li class="nav-item"><a class="nav-link js-scroll-trigger" href="#about">Come funziona</a></li>
                        <li class="nav-item"><a class="nav-link js-scroll-trigger" href="#account">Crea account</a></li>
                        <li class="nav-item"><a class="nav-link js-scroll-trigger" href="#moduli">Moduli</a></li>
                        <li class="nav-item"><a class="nav-link js-scroll-trigger" href="#contact">Contatti</a></li>
                        <li class="nav-item"><a class="nav-link js-scroll-trigger" href="./dashboard.php">Accedi</a></li>
                    </ul>
                </div>
            </div>
        </nav-->
        <!-- Masthead-->
        <?php
        require_once("header.php");
        require_once("come_funziona.php");
        ?>
        
        <!-- Account-->
        <section class="page-section bg-primary" id="account">
            <div class="container">
                <div class="row justify-content-center">
                    <div class="col-lg-8 text-center">
                        <h2 class="text-white mt-0">Inizia ad inserire i tuoi dati</h2>
                        <hr class="divider light my-4" />
                        <p class="text-white-50 mb-4">Compila il form per creare il tuo account, inserisci tutte le informazioni richieste e inizia subito a gestire in autonomia le tue istanze di CDU!</p>



                        <form id='login' action='./scelta_immobili.php#account' method='post' accept-charset='UTF-8'>
                        <input type='hidden' name='submitted' id='submitted' value='1'/>

                        <div class="form-group">
                        <label>Numero contratto*</label>
                        <input type="text" class="form-control" data-error="Il Numero contratto è obbligatorio, non può essere lasciato vuoto" name="num" required>
                        <div class="help-block with-errors"></div>
                        </div>



                        <div class="form-group">
                        <label>Cognome*</label>
                        <input type="text" class="form-control" data-error="Il Cognome è obbligatorio, non può essere lasciato vuoto" name="cognome" maxlength="16" required>
                        <div class="help-block with-errors"></div>
                        </div>

                        <div class="form-group">
                        <label>Nome*</label>
                        <input type="text" class="form-control" data-error="Il Nome è obbligatorio, non può essere lasciato vuoto" name="nome" maxlength="16" required>
                        <div class="help-block with-errors"></div>
                        </div>

                        <div class="form-group" style="text-align: justify;">
                            Il D.lgs. n. 196 del 30 giugno 2003 ("Codice in materia di protezione dei dati personali") prevede la tutela delle persone e di altri soggetti rispetto al trattamento dei dati personali. Secondo la normativa indicata, tale trattamento sarà improntato ai principi di correttezza, liceità e trasparenza e di tutela della Sua riservatezza e dei Suoi diritti. Ai sensi dell'articolo 13 del D.lgs. n.196/2003, pertanto, Le forniamo le seguenti informazioni: 
                            <ul>
                            <li> I dati da Lei forniti verranno trattati per attivare il mese di prova del servizio GisHosting </li>
                            <li> Il trattamento sarà effettuato in maniera automatizzata. 
                            <li> Il conferimento dei dati è obbligatorio poichè necessario per l’iscrizione sul servizio </li>
                            <li> I dati non saranno comunicati ad altri soggetti, né saranno oggetto di diffusione.</li>
                            </ul>
                            Acquisite le informazioni fornite dal titolare del trattamento, ai sensi dell'articolo 13 del D.Lgs. 196/2003, presta il suo consenso al trattamento dei dati personali per i fini indicati nella suddetta informativa? 
                            <br>
                            </div>
                            <input type="radio" id="consenso" name="consenso" value="consenso" required> Presto il consenso

                            
                            <hr class="light">
                            <!--input type='submit' name='Submit' value='Submit' /-->

                            <div class="form-group">
                            <button id="btnsubmit" type="submit" name='Submit' class="btn btn-light btn-xl" disabled>Invia</button>
                            </div>
                            </form>


                    </div>
                </div>
            </div>
        </section>
        <!-- Portfolio-->
        <!--div id="portfolio">
            <div class="container-fluid p-0">
                <div class="row no-gutters">
                    <div class="col-lg-4 col-sm-6">
                        <a class="portfolio-box" href="assets/img/portfolio/fullsize/1.jpg">
                            <img class="img-fluid" src="assets/img/portfolio/thumbnails/1.jpg" alt="" />
                            <div class="portfolio-box-caption">
                                <div class="project-category text-white-50">Category</div>
                                <div class="project-name">Project Name</div>
                            </div>
                        </a>
                    </div>
                    <div class="col-lg-4 col-sm-6">
                        <a class="portfolio-box" href="assets/img/portfolio/fullsize/2.jpg">
                            <img class="img-fluid" src="assets/img/portfolio/thumbnails/2.jpg" alt="" />
                            <div class="portfolio-box-caption">
                                <div class="project-category text-white-50">Category</div>
                                <div class="project-name">Project Name</div>
                            </div>
                        </a>
                    </div>
                    <div class="col-lg-4 col-sm-6">
                        <a class="portfolio-box" href="assets/img/portfolio/fullsize/3.jpg">
                            <img class="img-fluid" src="assets/img/portfolio/thumbnails/3.jpg" alt="" />
                            <div class="portfolio-box-caption">
                                <div class="project-category text-white-50">Category</div>
                                <div class="project-name">Project Name</div>
                            </div>
                        </a>
                    </div>
                    <div class="col-lg-4 col-sm-6">
                        <a class="portfolio-box" href="assets/img/portfolio/fullsize/4.jpg">
                            <img class="img-fluid" src="assets/img/portfolio/thumbnails/4.jpg" alt="" />
                            <div class="portfolio-box-caption">
                                <div class="project-category text-white-50">Category</div>
                                <div class="project-name">Project Name</div>
                            </div>
                        </a>
                    </div>
                    <div class="col-lg-4 col-sm-6">
                        <a class="portfolio-box" href="assets/img/portfolio/fullsize/5.jpg">
                            <img class="img-fluid" src="assets/img/portfolio/thumbnails/5.jpg" alt="" />
                            <div class="portfolio-box-caption">
                                <div class="project-category text-white-50">Category</div>
                                <div class="project-name">Project Name</div>
                            </div>
                        </a>
                    </div>
                    <div class="col-lg-4 col-sm-6">
                        <a class="portfolio-box" href="assets/img/portfolio/fullsize/6.jpg">
                            <img class="img-fluid" src="assets/img/portfolio/thumbnails/6.jpg" alt="" />
                            <div class="portfolio-box-caption p-3">
                                <div class="project-category text-white-50">Category</div>
                                <div class="project-name">Project Name</div>
                            </div>
                        </a>
                    </div>
                </div>
            </div>
        </div-->
        <!-- Scarica autocertificazioni -->
        <!--section class="page-section bg-dark text-white" id="moduli">
            <div class="container text-center">
                <h2 class="mb-4">Scarica i moduli per le autocertificazioni di pagamento</h2>
                <a style="margin-right:20px;" class="btn btn-light btn-xl" href="./download2.php">Diritti Istruttori</a>
                <a style="margin-left:20px;" class="btn btn-light btn-xl" href="./download.php">Marca da Bollo</a>
            </div>
        </section-->
<!-- Richiama fotter della pagina con contatti e librerie javascript-->
<?php
require('footer.php');
require('req_bottom.php');
?>



<!-- Script per abilitare il tasto invia solo se consenso checcato -->
<script> 
	$('#consenso').click(function () {
		//check if checkbox is checked
		if ($(this).is(':checked')) {
			$('#btnsubmit').removeAttr('disabled'); //enable input
		} else {
			$('#btnsubmit').attr('disabled', true); //disable input
		}
	});
</script>

    </body>
</html>
