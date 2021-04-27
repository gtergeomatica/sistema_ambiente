<?php
session_start();
$curPageName = substr($_SERVER["SCRIPT_NAME"],strrpos($_SERVER["SCRIPT_NAME"],"/")+1);
$user_admin="comuneisernia";
//$gruppo = 'comuneisernia3_group';
$cliente = 'Sistema Ambiente';


$cognome=pg_escape_string($_POST['cognome']);
$nome=pg_escape_string($_POST['nome']);
$num=pg_escape_string($_POST['num']);


require_once('../conn.php');


$query="SELECT codvia, indirizzo, civico, codimm, cod_via_comune FROM anagrafiche.aang_per_gis 
WHERE numcon=$1 and cognome ilike $2 and nome ilike $3";


$result = pg_prepare($conn, "myquery", $query);
$result = pg_execute($conn, "myquery", array($num, $cognome, $nome));

$check=0;
echo "<ul>";
while($r = pg_fetch_assoc($result)) {
    $check=$check+1;
    echo '<li>';
    echo 'Via '.$r["indirizzo"].' Numero civico: '.$r["civico"];
    echo ' <a href="civico.php?v='.$r["codvia"].'&c='.$r["civico"].'"';
    echo ' class="btn btn-info"> Scegli civico di esposizione </a>';
    echo '</li>';
    $civ=explode('/',$r_civico);
    $lungh=var_dump(count($civ));
    if ($lungh==1){
        $query_comune = "SELECT *, st_x(st_transform(geom,4326)) as lon, st_y(st_transform(geom,4326)) as lat
        FROM civici.t_civici
        WHERE codvia=$1 and num_civici=$2";
        $result2 = pg_prepare($conn, "myquery2", $query_comune);
        $result2 = pg_execute($conn, "myquery2", array($r['cod_via_comune'], $civ[0]));
        $check_civico=0;
        while($r2 = pg_fetch_assoc($result2)) {
            $check_civico=$check_civico+1;
            $lat=$r2['lat'];
            $lon=$r2['lon'];
        }
    } else if ($lungh==2){
        $query_comune = "SELECT *, st_x(st_transform(geom,4326)) as lon, st_y(st_transform(geom,4326)) as lat
        FROM civici.t_civici
        WHERE codvia=$1 and num_civici=$2 and esp_civ=$3";
        $result2 = pg_prepare($conn, "myquery2", $query_comune);
        $result2 = pg_execute($conn, "myquery2", array($r['cod_via_comune'], $civ[0], $civ[1]));
        $check_civico=0;
        while($r2 = pg_fetch_assoc($result2)) {
            $check_civico=$check_civico+1;
            $lat=$r2['lat'];
            $lon=$r2['lon'];
        }
    }
}

if ($check==0){
    echo "Non esistono immobili intestati a <b>".$cognome." ".$nome."</b> con numero di contratto <b>".$num."</b>";
}



?>