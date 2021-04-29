<?php
session_start();
$curPageName = substr($_SERVER["SCRIPT_NAME"],strrpos($_SERVER["SCRIPT_NAME"],"/")+1);
$user_admin="comuneisernia";
//$gruppo = 'comuneisernia3_group';
$cliente = 'Sistema Ambiente';


$cognome=pg_escape_string($_POST['cognome']);
$nome=pg_escape_string($_POST['nome']);
$num=pg_escape_string($_POST['num']);

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
        require_once("header.php");
        require_once("come_funziona.php");
        ?>
        
        <!-- Account-->
        <section class="page-section bg-primary" id="account">
            <div class="container">
                <div class="row justify-content-center">
                    <div class="col-lg-12 text-center">
                        <h2 class="text-white mt-0">Ricerca immobili di <?php echo $cognome?> <?php echo $nome;?> </h2>
                        <hr class="divider light my-4" />
                        <!--p class="text-white-50 mb-4">Compila il form per creare il tuo account, inserisci tutte le informazioni richieste e inizia subito a gestire in autonomia le tue istanze di CDU!</p-->
                        <?php
                        require_once('./conn.php');


                        $query="SELECT codvia, indirizzo, civico, codimm, ragso1, ragso2, cod_via_comune 
                        FROM anagrafiche.anag_per_gis 
                        WHERE numcon=$1 and trim(ragso1) ilike $2 and trim(ragso2) ilike $3";


                        $result = pg_prepare($conn, "myquery", $query);
                        $result = pg_execute($conn, "myquery", array($num, $cognome, $nome));

                        $check=0;
                        //echo "<ul>";
                        while($r = pg_fetch_assoc($result)) {
                            $check=$check+1;
                            echo '<h3>'.$r["indirizzo"].' Numero civico: '.$r["civico"];
                            //echo ' <br><a href="civico.php?v='.$r["codvia"].'&c='.$r["civico"].'"';
                            //echo ' class="btn btn-light"> Scegli civico di esposizione </a>';
                            echo '</h3>';
                            $civ=explode('/',$r['civico']);
                            //echo $civ[0];
                            $lungh=count($civ);
                            echo "<br>";
                            //echo $lungh;
                            // Cerco i civici del comune 
                            if ($lungh==1){
                                $query_comune = "SELECT st_x(st_transform(geom,4326)) as lon, st_y(st_transform(geom,4326)) as lat
                                FROM civici.t_civici
                                WHERE codvia=$1 and num_civici=$2;";
                                $result2 = pg_prepare($conn, "myquery2", $query_comune);
                                $result2 = pg_execute($conn, "myquery2", array(trim($r['cod_via_comune']), $civ[0]));
                                $check_civico=0;
                                
                                while($r2 = pg_fetch_assoc($result2)) {
                                    $check_civico=$check_civico+1;
                                    $lat=$r2['lat'];
                                    $lon=$r2['lon'];
                                }
                            } else if ($lungh==2){
                                $query_comune = "SELECT *, st_x(st_transform(geom,4326)) as lon, st_y(st_transform(geom,4326)) as lat
                                FROM civici.t_civici
                                WHERE codvia=$1::text and num_civici=$2 and esp_civ=$3";
                                $result2 = pg_prepare($conn, "myquery3", $query_comune);
                                $result2 = pg_execute($conn, "myquery3", array($r['cod_via_comune'], $civ[0], $civ[1]));
                                $check_civico=0;
                                while($r2 = pg_fetch_assoc($result2)) {
                                    $check_civico=$check_civico+1;
                                    $lat=$r2['lat'];
                                    $lon=$r2['lon'];
                                }
                            }
                            if ($check_civico==0){
                                // non ho trovato il civico (c=1) renindirizzo a una pagina dove l'utente può scegliere un altro civico 
                                echo 'Non trovo corrispondenza con il civico sullo stradario comunale';
                                echo ' <a href="correggi_civico.php?c=1&ci='.$r['codimm'].'&num='.$num.'&nome='.$nome.'&cognome='.$cognome.'"';
                                echo ' class="btn btn-secondary"> Scegli un altro civico o segnalaci dove si trova il tuo civico </a>';

                            } else if ($check_civico==1) {
                                //echo 'Il civico ha le seguenti coordinate '.$lat.' '.$lon.' ';
                                ?>

                                <div id="map"  style="width:100%; height: 500px;"></div>

                                <script>

                                var map = L.map('map', {scrollWheelZoom:false}).setView([<?php echo $lat;?>, <?php echo $lon;?>], 18);

                                L.tileLayer('http://{s}.tile.osm.org/{z}/{x}/{y}.png', {
                                    attribution: '&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors', 
                                    maxNativeZoom:19,
                                    maxZoom:25
                                }).addTo(map);

                                L.marker([<?php echo $lat;?> , <?php echo $lon;?>]).addTo(map)
                                    .bindPopup('<?php echo $r["indirizzo"].' '.$r["civico"]; ?> ')
                                    .openPopup();

                                </script>
                                <?php
                                echo ' <br><a href="civico.php?n='.$num.'v='.$r["codvia"].'&c='.$r["civico"].'"';
                                echo ' class="btn btn-success"> E\' il civico di esposizione </a>';
                                echo ' - ';
                                echo ' <a href="correggi_civico.php?c=0&num='.$num.'&nome='.$nome.'&cognome='.$cognome.'#about"';
                                echo ' class="btn btn-secondary"> Espongo in corrispondenza di altro civico </a>';
                            } else if ($check_civico==1) {
                                echo 'Civico multiplo su stradario comunale';
                            }
                        
                        
                        }
                        

                        if ($check==0){
                            echo "Non esistono immobili intestati a <b>".$cognome." ".$nome."</b> con numero di contratto <b>".$num."</b>";
                            echo "<br> Verifica di aver inserito correttamente i dati o che il tuo contratto TARI sia attivo.";
                        }
                        //echo "</ul>";

                        ?>


                    </div>
                </div>
            </div>
        </section>
        
<?php
require('footer.php');
require('req_bottom.php');
?>



    </body>
</html>
