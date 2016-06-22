<?php include '_header.php'; ?>

<div class="container">

    <div class="graphs">

        <h1>Restarting now...</h1>

        <?php
        $command = 'sudo service meterkast restart';
        system($command);
        ?>

        <a href="log.php">Continue to log</a>

    </div>

</div>

<?php include '_footer.php'; ?>