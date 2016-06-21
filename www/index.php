<?php include '_header.php'; ?>

<div class="container">

    <div class="graphs">

        <h1>Electriciteit</h1>

        <?php foreach(glob('electricity-*') as $file) : ?>
            <img src="<?php echo $file; ?>">
        <?php endforeach; ?>

        <h1>Gas</h1>

        <?php foreach(glob('gas-*') as $file) : ?>
            <img src="<?php echo $file; ?>">
        <?php endforeach; ?>

    </div>

</div>

<?php include '_footer.php'; ?>