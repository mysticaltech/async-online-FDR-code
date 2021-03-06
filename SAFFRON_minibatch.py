# SAFFRON mini-batch simulation code

import numpy as np


class SAFFRON_mini_proc_batch:
    def __init__(self, alpha0, numhyp, lbd, gamma_vec_exponent, batch_size):
        self.alpha0 = alpha0 # FDR level
        self.lbd = lbd


        # Compute the discount gamma sequence and make it sum to 1
        tmp = range(1, 10000)
        self.gamma_vec = np.true_divide(np.ones(len(tmp)),
                np.power(tmp, gamma_vec_exponent))
        self.gamma_vec = self.gamma_vec / np.float(sum(self.gamma_vec))

        self.w0 = (1 - lbd) * self.alpha0/2
        self.alpha = np.zeros(numhyp + 1) # vector of test levels alpha_t at every step
        self.alpha[0:2] = [0, self.gamma_vec[0] * self.w0]
        self.batch_size = batch_size


    def count_candidates(self, last_rej, candidates, timestep):
        ret_val = [];
        for j in range(1,len(last_rej)):
            ret_val = np.append(ret_val, sum(candidates[last_rej[j]+1:timestep + 1]))
        return ret_val.astype(int)



    def run_fdr(self, pvec):
        numhyp = len(pvec)
        last_rej = []
        rej = np.zeros(numhyp + 1)
        candidates = np.zeros(numhyp + 1)
        report = np.zeros(numhyp)

        for k in range(0, numhyp):

            # Get rejection indicators
            this_alpha = self.alpha[k + 1]
            rej[(int)(min(1000,np.ceil((k+1)/self.batch_size)*self.batch_size))] = rej[(int)(min(1000,np.ceil((k+1)/self.batch_size)*self.batch_size))] + (int)(pvec[k] < this_alpha)
            candidates[(int)(min(1000, np.ceil((k + 1) / self.batch_size) * self.batch_size))] = candidates[(int)(min(1000, np.ceil((k + 1) / self.batch_size) * self.batch_size))] + (int)(pvec[k] < self.lbd)
            report[k] = pvec[k]<this_alpha

            # Check first rejection
            if (rej[k + 1] >= 1):
                for t in range((int)(rej[k+1])):
                    last_rej = np.append(last_rej, k+1).astype(int)


            candidates_total = sum(candidates[0:k + 2])
            zero_gam = self.gamma_vec[k + 1 - (int)(candidates_total)]
            # Update alpha_t
            last_rej_sorted = np.array(sorted(last_rej))
            if len(last_rej) > 0:
                if last_rej_sorted[0]<= (k+1):
                    candidates_after_first = sum(candidates[last_rej_sorted[0]+1:k+2])
                    first_gam = self.gamma_vec[k + 1 - (last_rej_sorted[0]) - (int)(candidates_after_first)]
                else:
                    first_gam = 0
                if len(last_rej) >= 2:
                    sum_gam = self.gamma_vec[(k + 1) * np.ones(len(last_rej_sorted) - 1, dtype=int) - (last_rej_sorted[1:]) - self.count_candidates(last_rej_sorted, candidates, k + 1)]
                    indic = np.asarray(last_rej_sorted) <= (k + 1)
                    sum_gam = sum(np.multiply(sum_gam, indic[1:]))
                else:
                    sum_gam = 0
                next_alpha = min(self.lbd,
                                     zero_gam * self.w0 + ((1 - self.lbd) * self.alpha0 - self.w0) * first_gam + (
                                             1 - self.lbd) * self.alpha0 * sum_gam)
            else:
                next_alpha = min(self.lbd, zero_gam * self.w0)
            if k < numhyp - 1:
                self.alpha[k + 2] = next_alpha



        self.alpha = self.alpha[1:]
        return report

