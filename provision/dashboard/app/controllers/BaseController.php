<?php

class BaseController extends Controller {

    protected $layout = 'base';

    const PAGE_SCORES = 'scores';
    const PAGE_DIAGNOSTICS = 'diagnostics';
    const PAGE_LOGIN = 'login';

    /**
     * Setup the layout used by the controller.
     *
     * @return void
     */
    protected function setupLayout()
    {
        $this->layout = View::make($this->layout);
    }

}
