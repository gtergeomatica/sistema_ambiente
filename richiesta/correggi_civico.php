<?php
session_start();
$curPageName = substr($_SERVER["SCRIPT_NAME"],strrpos($_SERVER["SCRIPT_NAME"],"/")+1);
$user_admin="comuneisernia";
//$gruppo = 'comuneisernia3_group';
$cliente = 'Sistema Ambiente';

$c=pg_escape_string($_GET['c']);
if ($c==1) {
    $codimm=pg_escape_string($_GET['ci']);  
}
$cognome=pg_escape_string($_GET['cognome']);
$nome=pg_escape_string($_GET['nome']);
$num=pg_escape_string($_GET['num']);


?>


<!DOCTYPE html>
<html lang="en">
    <head>
        <meta charset="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no" />
        <meta name="description" content="" />
        <meta name="author" content="" />
        <title>Scelta immobili </title>
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
        
        <!-- Masthead-->
        <?php
        //require_once("header.php");
        //require_once("come_funziona.php");
        
        
        
        ?>
        
        <!-- Account-->
        <section class="page-section bg-primary" id="account">
            <div class="container">
                <div class="row justify-content-center">
                    <div class="col-lg-12 text-center">
                    <?php
                        require_once('./conn.php');
                        if ($c==1){

                            $query="SELECT codvia, indirizzo, civico, codimm, ragso1, ragso2, cod_via_comune 
                                        FROM anagrafiche.anag_per_gis 
                                        WHERE numcon=$1 and trim(ragso1) ilike $2 and trim(ragso2) ilike $3";
                
                
                                        $result = pg_prepare($conn, "myquery", $query);
                                        $result = pg_execute($conn, "myquery", array($num, $cognome, $nome));
                
                                        $check=0;
                                        //echo "<ul>";
                                        while($r = pg_fetch_assoc($result)) {
                                            $check=$check+1;
                                            $indirizzo=$r["indirizzo"];
                                            $civico=$r["civico"];
                                            echo ''.$r["indirizzo"].' Numero civico: '.$r["civico"];
                                            //echo ' <br><a href="civico.php?v='.$r["codvia"].'&c='.$r["civico"].'"';
                                            //echo ' class="btn btn-light"> Scegli civico di esposizione </a>';
                                            //echo '</h3>';
                                        }
                                        echo '<br> Il fatto che non si trovi corrispondenza pu?? dipendere dal fatto che l\'indirizzo che leggi qua sopra non sia corretto <a href"#civici"> selezionane </a> uno corretto, oppure dal fatto che non ci sia il suo civico sullo stradario comunale. In tal caso cercalo sulla mappa e indicaci la corretta posizione.
                                        ';
                        }

                        ?>

                        <hr class="divider light my-4" />
                        <h2 id="civici" class="text-white mt-0">Ricerca civici stradario comunale</h2>
                        <hr class="divider light my-4" />
                        <!--p class="text-white-50 mb-4">Compila il form per creare il tuo account, inserisci tutte le informazioni richieste e inizia subito a gestire in autonomia le tue istanze di CDU!</p-->
                        
                        <form id="form_civici" method="post" class="form-horizontal">

                        <input type="hidden" name="num" value="<?php echo $num;?>"/>
                        <input type="hidden" name="nome" value="<?php echo $nome;?>"/>
                        <input type="hidden" name="cognome" value="<?php echo $cognome;?>"/>
                        <script>
                        function getCivico(val) {
                            $.ajax({
                            type: "POST",
                            url: "get_civico.php",
                            data:'cod='+val,
                            success: function(data){
                                $("#civico-list").html(data);
                            }
                            });
                        }

                        </script>

                


                        <div class="form-group  ">
                        <label for="via">Via:</label> *
                            <select id="via-list" class="selectpicker show-tick form-control" data-live-search="true" onChange="getCivico(this.value);" required="">
                            <option value="">Seleziona la via</option>
            <?php            
            $query2="SELECT distinct codvia, concat(specie, ' ', den) as desvia 
            FROM civici.t_civici order by 2;";
	        $result2 = pg_query($conn, $query2);
            //echo $query1;    
            while($r2 = pg_fetch_assoc($result2)) { 
                $valore=  $r2['codvia']. ";".$r2['desvia'];            
            ?>
                        
                    <option name="codvia" value="<?php echo $r2['codvia'];?>" ><?php echo $r2['desvia'];?></option>
             <?php } ?>

             </select>            
             </div>

                        <div class="form-group">
                        <label for="id_civico">Civico:</label> *
                            <select class="form-control" name="id_civico" id="civico-list" class="demoInputBox" required="">
                            <option value="">Seleziona il civico</option>
                        </select> 
                        </div>

                        <button id="btnsubmit" type="submit" name='Submit' class="btn btn-light btn-xl">Invia</button>
                        </form>
                    <?php
                    if ($c==0){
                        echo '<br><small> Ricorda che ?? possibile scegliere solo civici presenti nello stradario comunale! 
                        Se non trovi corrispondenza, devi usare il tuo civico, o contattarci per maggiori informazioni'; 
                        ?>

                        <!--a style="color:white;" href="scelta_immobili.php?num='.$num.'&nome='.$nome.'&cognome='.$cognome.'">
                        torna indietro</a-->
                        
                        <form action="scelta_immobili.php#about" method="post">
                        <input type="hidden" name="num" value="<?php echo $num;?>"/>
                        <input type="hidden" name="nome" value="<?php echo $nome;?>"/>
                        <input type="hidden" name="cognome" value="<?php echo $cognome;?>"/>
                        <button type="submit" name="your_name" value="your_value" class="btn-link">tornando indietro</button>
                        </form>
                        <?php
                        //echo 'e usa il tuo civico.</small>'; 
                    } else {
                    ?>
                    <hr class="divider light my-4" />
                    <h2 id="civici" class="text-white mt-0">Ricerca civici stradario comunale</h2>
                    <hr class="divider light my-4" />
                        <form id="form_mappa" method="post" class="form-horizontal">
                        <input type="hidden" name="via" value="<?php echo $indirizzo;?>"/>
                        <input type="hidden" name="civico" value="<?php echo $civico
                        ;?>"/>

                        <div class="form-group">
                            <label for="lat"> Latitudine </label> <font color="red">*</font>
                            <input readonly="" type="text" name="lat" id="lat" class="form-control" required="">
                        </div>
                                
                                <div class="form-group">
                            <label for="lon"> Longitudine </label> <font color="red">*</font>
                            <input readonly="" type="text" name="lon" id="lon" class="form-control" required="">
                        </div>
                        <div id="mapid" style="width: 100%; height: 600px;"></div>
                        <button id="btnsubmit2" type="submit" name='Submit' class="btn btn-light btn-xl">Invia</button>
                        </form>

                    <?php
                    }
                    ?>
                    </div>
                </div>
            </div>
        </section>
        
<?php
require('mappa_georef.php');
require('footer.php');
require('req_bottom.php');
?>



    </body>
</html>
