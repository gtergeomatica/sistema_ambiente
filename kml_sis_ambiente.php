<?php 
$col = pg_escape_string($_GET['c']);
$giro = pg_escape_string($_GET['g']);
header("Content-Disposition: attachment; filename=".$col."_".$giro.".kml");
require('./conn.php');

if(!$conn) {
    die('Connessione fallita !<br />');
} else {
	
	//echo "OK";
    

	$query="SELECT st_asKML(geom) as geo FROM percorsi.v_giri g WHERE zona=$1 AND giro=$2;";
    
    //echo $query;
	$result = pg_prepare($conn, "my_query", $query);
    $result = pg_execute($conn, "my_query", array($col, $giro));
    #echo $result;
	#echo $query;
	#exit;
	#$rows = array();
	$kml='<?xml version="1.0" encoding="utf-8" ?>
    <kml xmlns="http://www.opengis.net/kml/2.2">
    <Document id="'.$col.'_'.$giro.'">
    <Schema name="'.$col.'_'.$giro.'" id="'.$col.'_'.$giro.'">
        <SimpleField name="id" type="float"></SimpleField>
    </Schema>
    <Folder><name>'.$col.'_'.$giro.'</name>
      <Placemark>
      ';
      if ($col=='R'){
        $kml = $kml .'<Style><LineStyle><color>ff0000ff</color></LineStyle><PolyStyle><fill>0</fill></PolyStyle></Style>';
      } else if  ($col=='B'){
        $kml = $kml .'<Style><LineStyle><color>0000ffff</color></LineStyle><PolyStyle><fill>0</fill></PolyStyle></Style>';
    } else if  ($col=='G') {
        $kml = $kml .'<Style><LineStyle><color>ff0000ff</color></LineStyle><PolyStyle><fill>0</fill></PolyStyle></Style>';
      }
        $kml = $kml .'
            <ExtendedData><SchemaData schemaUrl="#'.$col.'_'.$giro.'">
            <SimpleData name="id">'.$col.'_'.$giro.'</SimpleData>
        </SchemaData></ExtendedData>
        ';
    while($r = pg_fetch_assoc($result)) {
    	#$rows[] = $r;
        
        $kml= $kml .''. $r['geo'];
	}
    $kml= $kml . ' </Placemark>
    </Folder>
    </Document></kml>';
    print $kml;
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