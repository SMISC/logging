<?php

class BaseController extends Controller {

    protected $layout = 'base';

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
