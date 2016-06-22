<?php include '_header.php'; ?>

    <div class="container-fluid">

        <div class="graphs">

            <h1>Log</h1>

            <?php

            $log = file('/home/pi/code/var/meterkast.log');
            $log = array_reverse($log);

            foreach($log as $line) :
                echo $line . '<br>';
            endforeach;

            ?>

        </div>

    </div>

<?php include '_footer.php'; ?>