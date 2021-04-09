<?php 

require('./conn.php');

if(!$conn) {
    die('Connessione fallita !<br />');
} else {
	$col = pg_escape_string($_GET['c']);
    $giro = pg_escape_string($_GET['g']);
	
	$query="SELECT st_asKML(geom) 
    FROM percorsi.v_giri g 
    WHERE zona=$1 AND giro=$2;";
    
    //echo $query;
	$result = pg_prepare($conn, "my_query", $query);
    $result = pg_execute($conn, "my_query", array($col, $giro));

	#echo $query;
	#exit;
	#$rows = array();
	while($r = pg_fetch_assoc($result)) {
    	#$rows[] = $r;
        echo $r[0];
	}
	pg_close($conn);
	#echo $rows ;
	/*if (empty($rows)==FALSE){
		//print $rows;
		print json_encode(array_values(pg_fetch_all($result)));
	} else {
		echo "[{\"NOTE\":'No data'}]";
	}*/
}

?>