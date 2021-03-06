import time
import os
from visa import *
from pyvisa.resources.gpib import _GPIBMixin
from pyvisa.resources.messagebased import MessageBasedResource

def read_stb_with_previous(self, previous=False):
    """
    Read service request status byte.
    :param self:
    :param previous: If previous=True, the value of stb from the latest call with previous=False is retrieved.
    :return: status byte
    """
    if(os.name == 'posix'):
        value, retcode = self.visalib.read_stb(self.session, previous)
    else:
        value, retcode = self.visalib.read_stb(self.session)
    return value

@Resource.register(constants.InterfaceType.gpib, 'INSTR')
class GPIBInstrument(_GPIBMixin, MessageBasedResource):
    """Communicates with to devices of type GPIB::<primary address>[::INSTR]

    More complex resource names can be specified with the following grammar:
        GPIB[board]::primary address[::secondary address][::INSTR]

    Do not instantiate directly, use :meth:`pyvisa.highlevel.ResourceManager.open_resource`.
    """

    def wait_for_srq(self, timeout=25000):
        """Wait for a serial request (SRQ) coming from the instrument.

        Note that this method is not ended when *another* instrument signals an
        SRQ, only *this* instrument.

        :param timeout: the maximum waiting time in milliseconds.
                        Defaul: 25000 (milliseconds).
                        None means waiting forever if necessary.
        """
        self.enable_event(constants.VI_EVENT_SERVICE_REQ, constants.VI_QUEUE)
        stb = 0
        timeout = self.timeout

        if timeout and not (0 <= timeout <= 4294967295):
            raise ValueError("timeout value is invalid")

        starting_time = time.clock()

        while True:
            if timeout is None:
                adjusted_timeout = constants.VI_TMO_INFINITE
            else:
                adjusted_timeout = int((starting_time + timeout / 1e3 - time.clock()) * 1e3)
                if adjusted_timeout < 0:
                    adjusted_timeout = 0

            rsp = self.wait_on_event(constants.VI_EVENT_SERVICE_REQ, adjusted_timeout)
            if rsp.timed_out == False:
                if (os.name == 'posix'):
                    stb = self.read_stb(previous=True)
                else:
                    stb = self.stb

                if stb & 0x40:
                    break
            else:
                self.disable_event(constants.VI_EVENT_SERVICE_REQ, constants.VI_QUEUE)
                raise VisaIOError(constants.StatusCode.error_timeout)

        self.disable_event(constants.VI_EVENT_SERVICE_REQ, constants.VI_QUEUE)
        return stb