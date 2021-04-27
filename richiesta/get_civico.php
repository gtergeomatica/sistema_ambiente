<?php
session_start();
//require('../validate_input.php');;



include "conn.php";
if(!empty($_POST["cod"])) {
    $query = "SELECT id, concat(specie, ' ', den) as nome, 
    concat(num_civici, ' ', esp_civ) as civico  
    FROM civici.t_civici where codvia='".$_POST["cod"]."' ORDER BY 3;";
    #echo $query;
    $result = pg_query($conn, $query);

     while($r = pg_fetch_assoc($result)) { 
    ?>

        <option name="id_civico" value="<?php echo $r['id'];?>" ><?php echo $r['civico'];?></option>
<?php
    }
}
?>