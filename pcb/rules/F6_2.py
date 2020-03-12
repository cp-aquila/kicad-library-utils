# -*- coding: utf-8 -*-

from __future__ import division

from rules.rule import *
from math import sqrt

class Rule(KLCRule):
    """
    Create the methods check and fix to use with the kicad_mod files.
    """
    def __init__(self, module, args):
        super(Rule, self).__init__(module, args,'For surface-mount devices, footprint anchor is placed in the middle of the footprint (IPC-7351).')

    def check(self):
        """
        Proceeds the checking of the rule.
        The following variables will be accessible after checking:
            * center_pads
            * center_fab
        """
        module = self.module
        if module.attribute != 'smd':
            # Ignore non-smd parts
            return False

        center_pads = module.padMiddlePosition()
        center_fab  = module.geometricBoundingBox("F.Fab").center

        err = False

        # calculate the distance from origin for the pads and fab
        diff_pads = sqrt(center_pads['x']**2 + center_pads['y']**2)
        diff_fab  = sqrt(center_fab['x']**2 +  center_fab['y']**2)
        # select the xy coordinates that are closest to the center
        if diff_pads > diff_fab:
            (x, y) = (center_fab['x'], center_fab['y'])
        else:
            (x, y) = (center_pads['x'], center_pads['y'])

        THRESHOLD = 0.001
        if abs(x) > THRESHOLD or abs(y) > THRESHOLD:
            self.error("Footprint anchor is not located at center of footprint")
            self.errorExtra("Footprint center calculated as Pad: ({xp},{yp})mm F.Fab: ({xf}, {yf})mm".format(
                xp = round(center_pads['x'], 5),
                yp = round(center_pads['y'], 5),
                xf = round(center_fab['x'], 5),
                yf = round(center_fab['y'], 5)))
            if center_pads['x'] != center_fab['x'] or center_pads['y'] != center_fab['y']:
                self.errorExtra("Footprint centers of pads and F.Fab do not match")

            err = True

        return err

    def fix(self):
        """
        Proceeds the fixing of the rule, if possible.
	This fix will always use the pads center position.
        """
        module = self.module
        if self.check():
            self.info("Footprint anchor fixed")

            center = module.padMiddlePosition()

            module.setAnchor([center['x'], center['y']])
