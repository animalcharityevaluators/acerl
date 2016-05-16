<?php/* * Welcome section */$mp_emmet_welcome_animation_left = esc_attr(get_theme_mod('theme_welcome_animation_left', 'fadeInLeft'));$mp_emmet_welcome_animation_right = esc_attr(get_theme_mod('theme_welcome_animation_right', 'fadeInRight'));?><section id="welcome" class="welcome-section white-section">    <div class="container">        <div class="row">            <div class="col-xs-12 col-sm-6 col-md-6 col-lg-6">                <?php if ($mp_emmet_welcome_animation_left === 'none'): ?>                    <div class="section-content">                    <?php else: ?>                        <div class="section-content animated anHidden"  data-animation="<?php echo $mp_emmet_welcome_animation_left; ?>">                        <?php endif; ?>                        <?php                        $mp_emmet_welcome_title = esc_html(get_theme_mod('theme_welcome_title'));                        $mp_emmet_welcome_description = esc_html(get_theme_mod('theme_welcome_description'));                        $mp_emmet_welcome_button_label = esc_html(get_theme_mod('theme_welcome_button_label'));                        $mp_emmet_welcome_button_url = esc_url(get_theme_mod('theme_welcome_button_url'));                        if (get_theme_mod('theme_welcome_title', false) === false) :                            ?>                             <h2 class="section-title"><?php _e('WordPress Customizer', 'emmet-lite'); ?></h2>                            <?php                        else:                            if (!empty($mp_emmet_welcome_title)):                                ?>                                <h2 class="section-title"><?php echo $mp_emmet_welcome_title; ?></h2>                                <?php                            endif;                        endif;                        if (get_theme_mod('theme_welcome_description', false) === false) :                            ?>                             <div class="section-description"><?php _e('Build blocks, change theme colors, edit titles, manage widgets and see the results of the changes in real time. Make some pretty unique site designs without touching any code.', 'emmet-lite'); ?></div>                            <?php                        else:                            if (!empty($mp_emmet_welcome_description)):                                ?>                                <div class="section-description"><?php echo $mp_emmet_welcome_description; ?></div>                                <?php                            endif;                        endif;                        ?>                        <div class="section-buttons">                            <?php                            if (get_theme_mod('theme_welcome_button_label', false) === false) :                                ?>                                <a href="#welcome" title="<?php _e('read more', 'emmet-lite') ?>" class="button"><?php _e('read more', 'emmet-lite') ?></a>                                <?php                            else:                                if (!empty($mp_emmet_welcome_button_label) && !empty($mp_emmet_welcome_button_url)):                                    ?>                                    <a href="<?php echo $mp_emmet_welcome_button_url; ?>" title="<?php echo $mp_emmet_welcome_button_label; ?>" class="button"><?php echo $mp_emmet_welcome_button_label; ?></a>                                    <?php                                endif;                            endif;                            ?>                        </div>                    </div>                </div>                <?php if ($mp_emmet_welcome_animation_right === 'none'): ?>                    <div class="section-right welcome-right">                    <?php else: ?>                        <div class="section-right welcome-right animated anHidden"   data-animation="<?php echo $mp_emmet_welcome_animation_right; ?>">                        <?php endif; ?>                    </div>                </div>                </section><?php