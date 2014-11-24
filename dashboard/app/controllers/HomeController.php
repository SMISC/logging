<?php

class HomeController extends BaseController
{
    public function showOverview()
    {
        return View::make('overview');
    }
}
